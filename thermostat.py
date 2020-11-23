#!/usr/bin/env python3

import tkinter as tk
import tkinter.font as font


class Application:
    def __init__(self, window):
        self.window = window
        canvas = tk.Canvas(window)
        canvas.pack(expand=True, fill=tk.BOTH)
        canvas.update()
        self.canvas = canvas
        self.add_widgets()
        canvas.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.buttons_frame.config(width=event.height // 4)

    def add_widgets(self):
        height = self.canvas.winfo_height()

        self.info_frame = tk.Frame(self.canvas, bg="red")
        self.info_frame.pack(expand=True, fill=tk.BOTH, side=tk.LEFT)
        # info_frame.update()

        self.buttons_frame = tk.Frame(self.canvas, bg="blue",  width=height//4)
        self.buttons_frame.pack_propagate(0)
        self.buttons_frame.pack(expand=False, fill=tk.BOTH, side=tk.RIGHT)

        myFont = font.Font(size=30)
        # button_up = tk.Button(self.buttons_frame, text="\u02c4", bg="yellow")
        # button_up = tk.Button(self.buttons_frame, text="\u2227", bg="yellow")
        button_up = tk.Button(self.buttons_frame, text="\u2303", bg="yellow")
        button_up.pack(expand=True, fill=tk.BOTH)
        button_up.config(font = myFont)

        # button_down = tk.Button(self.buttons_frame, text="\u02c5", bg="yellow")
        # button_down = tk.Button(self.buttons_frame, text="\u2228", bg="yellow")
        button_down = tk.Button(self.buttons_frame, text="\u2304", bg="yellow")
        button_down.pack(expand=True, fill=tk.BOTH)
        button_down.config(font = myFont)

        button_onoff = tk.Button(
            self.buttons_frame, text="\u23fc", bg="yellow")
        button_onoff.pack(expand=True, fill=tk.BOTH)
        button_onoff.config(font = myFont)

        button_configure = tk.Button(
            self.buttons_frame, text="\u2328", bg="yellow")
        button_configure.pack(expand=True, fill=tk.BOTH)
        button_configure.config(font = myFont)


def main():
    window = tk.Tk()
    window.title("Thermostat v0.1")
    window.geometry("800x400")
    # window.state("zoomed")
    Application(window)
    window.mainloop()


if __name__ == '__main__':
    main()
