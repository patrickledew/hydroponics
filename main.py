# Setup API

from flask import Flask, request, jsonify
from flask_cors import CORS
from motor import MotorDriver
from sensor import MoistureSensor
import asyncio
import threading

from schedule_manager import ScheduleManager
from worker import worker

app = Flask(__name__)
cors = CORS(app)
pump = MotorDriver()
sensor = MoistureSensor()
schedule_manager = ScheduleManager()


async def startup_test():
    await pump.run_for(1.0, 0.5)
    await pump.run_for(-1.0, 0.5)
    await pump.run_for(1.0, 0.5)
    await pump.run_for(-1.0, 0.5)
    await pump.run_for(1.0, 0.5)
asyncio.get_event_loop().run_until_complete(startup_test())

# Start worker process in a separate thread
def run_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(worker(pump, sensor))


worker_thread = threading.Thread(target=run_worker, daemon=True)
worker_thread.start()

@app.route("/api/pump/<speed>/<duration>")
async def run_pump(speed, duration):
    speed = float(speed)
    duration = float(duration)
    print("Running for " + str(duration) + " seconds at speed " + str(speed))
    await pump.run_for(speed, duration)
    return "<h1>Pump ran for " + str(duration) + " seconds at speed " + str(speed) + "</h1>"

@app.route("/api/moisture")
async def get_moisture():
    print("Moisture: " + str(sensor.read_value()))
    return {
        "value": sensor.read_value()
    }

# Schedule API endpoints
@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    schedules = schedule_manager.get_all()
    return jsonify([s.to_dict() for s in schedules])

@app.route('/api/schedules/<schedule_id>', methods=['GET'])
def get_schedule(schedule_id):
    schedule = schedule_manager.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify(schedule.to_dict())

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    print(request)
    data = request.json
    print(data)
    schedule = schedule_manager.create(data)
    return jsonify(schedule.to_dict()), 201

@app.route('/api/schedules/<schedule_id>', methods=['PUT'])
def update_schedule(schedule_id):
    data = request.json
    schedule = schedule_manager.update(schedule_id, data)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify(schedule.to_dict())

@app.route('/api/schedules/<schedule_id>', methods=['DELETE'])
def delete_schedule(schedule_id):
    success = schedule_manager.delete(schedule_id)
    if not success:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify({"success": True})

@app.route('/api/schedules/<schedule_id>/activate', methods=['PUT'])
def activate_schedule(schedule_id):
    success = schedule_manager.activate(schedule_id)
    if not success:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify({"success": True})

@app.route('/api/schedules/<schedule_id>/deactivate', methods=['PUT'])
def deactivate_schedule(schedule_id):
    success = schedule_manager.deactivate(schedule_id)
    if not success:
        return jsonify({"error": "Schedule not found"}), 404
    return jsonify({"success": True})

@app.route('/api/schedules/<schedule_id>/trigger', methods=['POST'])
def trigger_schedule(schedule_id):
    schedule = schedule_manager.get(schedule_id)
    if not schedule:
        return jsonify({"error": "Schedule not found"}), 404
    
    # Start a separate thread to handle the pump activation
    def activate_pump():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(pump.activate(schedule.pump_duration_seconds))
        schedule_manager.record_watering(schedule_id)
    
    threading.Thread(target=activate_pump).start()
    return jsonify({"success": True})
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)