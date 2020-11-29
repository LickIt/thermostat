#!/usr/bin/env node
const http = require("http");
const sensorLib = require("node-dht-sensor").promises;

const sensorType = 22; // 11 for DHT11, 22 for DHT22 and AM2302
const sensorPin  = 4;  // The GPIO pin number for sensor signal

const requestListener = function (req, res) {
    var readout = sensorLib.read(sensorType, sensorPin).then(
        function(data) {
            res.writeHead(200);
            res.end(JSON.stringify({
                temperature: +data.temperature.toFixed(1),
                humidity: +data.humidity.toFixed(1)
            }));
        },
        function(err) {
            res.writeHead(500);
            res.end(JSON.stringify({ error: err.toString() }));
        }
    );
}

const server = http.createServer(requestListener);
server.listen(8080);