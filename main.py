# Setup API

from flask import Flask
from flask_cors import CORS
from motor import MotorDriver
from sensor import MoistureSensor
import asyncio
from asyncio import create_task
from types import CoroutineType
app = Flask(__name__)
cors = CORS(app)
pump = MotorDriver()
sensor = MoistureSensor()

current_task = None

@app.route("/pump/<speed>/<duration>")
async def run_pump(speed, duration):
    speed = float(speed)
    duration = float(duration)
    print("Running for " + str(duration) + " seconds at speed " + str(speed))
    await pump.run_for(speed, duration)
    return "<h1>Pump ran for " + str(duration) + " seconds at speed " + str(speed) + "</h1>"

@app.route("/moisture")
async def get_moisture():
    print("Moisture: " + str(sensor.read_value()))
    return {
        "value": sensor.read_value()
    }


asyncio.run(pump.run_for(1,1))