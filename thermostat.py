#!/usr/bin/env python3

import logging
import time
import json
import tkinter as tk
import tkinter.font as font
import urllib.request
from threading import Timer
from typing import Callable, Any, Optional

# adafruit-blinka
import board
from digitalio import DigitalInOut, Direction


class Application:
    measure_interval = 30
    process_interval = 10000

    def __init__(self, window: tk.Tk, relay: DigitalInOut):
        self.window = window
        self.relay = relay
        self.relay_on = False
        self.power_on = False
        self.power_button: tk.Button = None
        self.temperature: Optional[float] = None
        self.humidity: Optional[float] = None
        self.temperature_label = tk.StringVar()
        self.humidity_label = tk.StringVar()
        self.error_label = tk.StringVar()
        self.lastSuccessfulMeasure = time.time()
        self.logger = self.create_logger()
        self.target_temp = 24.0
        self.target_temp_label = tk.StringVar(value=str(self.target_temp) + "\u00B0")

        self.canvas = self.create_canvas(window)
        self.info_frame = self.create_info_frame()
        self.buttons_frame = self.create_buttons_frame()
        self.canvas.bind("<Configure>", self.on_resize)

        Timer(0, self.read_sensor_data).start()
        self.window.after(5000, self.process_sensor_data)

    @staticmethod
    def create_logger() -> logging.Logger:
        logger = logging.getLogger("thermostat")
        logger.setLevel(logging.INFO)
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

        file_handler = logging.FileHandler("/tmp/thermostat.log", mode="a")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

        return logger

    @staticmethod
    def create_canvas(window: tk.Tk) -> tk.Canvas:
        canvas = tk.Canvas(window)
        canvas.pack(expand=True, fill=tk.BOTH)
        canvas.update()

        return canvas

    def on_resize(self, event):
        self.buttons_frame.config(width=event.height // 4)

    def create_info_frame(self) -> tk.Frame:
        info_frame = tk.Frame(self.canvas, bg="white")
        info_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)

        readings_frame = tk.Frame(info_frame, bg="white", bd=2)
        readings_frame.place(y=0, relheight=0.5, relwidth=0.7)
        readings_frame.update()

        target_frame = tk.Frame(info_frame, bg="white")
        target_frame.place(y=0, relx=0.7, relheight=0.5, relwidth=0.3)
        target_frame.update()

        error_frame = tk.Frame(info_frame, bg="white")
        error_frame.place(rely=0.9, relheight=0.1, relwidth=1)

        readings_frame_height = readings_frame.winfo_height()
        tk.Label(readings_frame, textvariable=self.temperature_label, bg="white",
                 font=font.Font(size=int(readings_frame_height * 0.4))).pack(side=tk.TOP)
        tk.Label(readings_frame, textvariable=self.humidity_label, bg="white",
                 font=font.Font(size=int(readings_frame_height * 0.25))).pack(side=tk.TOP)

        tk.Label(target_frame, textvariable=self.target_temp_label, bg="white",
                 font=font.Font(size=int(target_frame.winfo_height() * 0.2))).pack(expand=True, fill=tk.BOTH)

        tk.Label(error_frame, fg="#c62828", font=font.Font(size=15), bg="white", textvariable=self.error_label).pack(
            expand=True, fill=tk.BOTH)

        return info_frame

    def create_buttons_frame(self) -> tk.Frame:
        height: int = self.canvas.winfo_height()

        buttons_frame = tk.Frame(self.canvas, width=height // 4)
        buttons_frame.pack_propagate(0)
        buttons_frame.pack(expand=False, fill=tk.BOTH, side=tk.RIGHT)

        self.add_button(buttons_frame, "\u25B3", self.temp_up)
        self.add_button(buttons_frame, "\u25BD", self.temp_down)
        self.power_button = self.add_button(buttons_frame, "OFF", self.toggle_power, fg="gray")
        self.add_button(buttons_frame, "\u2328", None)

        return buttons_frame

    @staticmethod
    def add_button(parent, text, command: Callable, font_size=30, fg="black") -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=font.Font(size=font_size),
            fg=fg,
            highlightbackground="black",
            bg="white"
        )
        button.pack(expand=True, fill=tk.BOTH)

        return button

    def temp_up(self):
        self.target_temp += 0.5
        self.target_temp_label.set(str(self.target_temp) + "\u00B0")

    def temp_down(self):
        self.target_temp -= 0.5
        self.target_temp_label.set(str(self.target_temp) + "\u00B0")

    def toggle_power(self):
        if self.power_on:
            self.relay_stop()
            self.power_on = False
            self.power_button.config(text="OFF", fg="gray")
            self.logger.info("Power off")
        else:
            self.power_on = True
            self.power_button.config(text="ON", fg="green")
            self.logger.info("Power on")

    def relay_start(self):
        self.relay.value = 0
        self.relay_on = True
        self.logger.info("Relay on")

    def relay_stop(self):
        self.relay.value = 1
        self.relay_on = False
        self.logger.info("Relay off")

    def read_sensor_data(self):
        try:
            with urllib.request.urlopen("http://localhost:8080") as response:
                data = json.loads(response.read())
                print(data)
                self.temperature = data["temperature"]
                self.humidity = data["humidity"]
                self.lastSuccessfulMeasure = time.time()
        except Exception as e:
            self.logger.error(e)

        timer = Timer(self.measure_interval, self.read_sensor_data)
        timer.daemon = True
        timer.start()

    def process_sensor_data(self):
        delta_t = time.time() - self.lastSuccessfulMeasure
        if delta_t > 180:
            self.logger.warning("Temperature sensor data older than %ss", int(delta_t))
            if self.power_on:  # power off on unknown temperature
                self.toggle_power()
            self.show_error("E01 - No sensor data")
        else:
            self.adjust_temperature()
            self.update_labels()

        self.window.after(self.process_interval, self.process_sensor_data)

    def adjust_temperature(self):
        delta_t = 0.5
        if self.power_on:
            if self.relay_on and self.temperature > self.target_temp + delta_t:
                self.relay_stop()
            elif not self.relay_on and self.temperature < self.target_temp - delta_t:
                self.relay_start()

    def update_labels(self):
        if self.temperature:
            suffix = "\u00B0"
            if self.relay_on:
                suffix += "\u2191"
            self.temperature_label.set(str(self.temperature) + suffix)

        if self.humidity:
            self.humidity_label.set(str(self.humidity) + "%")

    def show_error(self, error: Optional[str] = None):
        self.error_label.set(error)


def main():
    # relay - pin 38 physical = BCM 20
    relay = DigitalInOut(board.D20)
    relay.direction = Direction.OUTPUT
    relay.value = 1  # OFF

    window = tk.Tk()
    window.title("Thermostat v0.1")
    # window.geometry("800x400")
    # Application(window, None)
    window.attributes("-zoomed", True)
    Application(window, relay)
    try:
        window.mainloop()
    finally:
        relay.value = 1  # OFF
        # pass


if __name__ == '__main__':
    main()
