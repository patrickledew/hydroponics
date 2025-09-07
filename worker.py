# Worker process for handling long-running tasks, including checking moisture levels and activating the pump.
import asyncio
import threading
import datetime
import time

from motor import MotorDriver
from sensor import MoistureSensor
from schedule_manager import ScheduleManager
import os

def moisture_history_string(moisture_readings, minutes=60):
    """Generate a string representation of moisture readings over the past given minutes."""
    cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
    recent_readings = [r for r in moisture_readings if r[0] >= cutoff_time]
    if not recent_readings:
        return "* No readings in the past {minutes}m."
    
    chars = " ▁▂▃▄▅▆▇█"
    graph_length = 30
    history_str = f"* Last {minutes}m:"
    for i in range(graph_length):
        index = int(i * len(recent_readings) / graph_length)
        if index >= len(recent_readings):
            break
        level = recent_readings[index][1]
        history_str += chars[min(level // 10, 9)]
    return history_str

async def worker(pump: MotorDriver, sensor: MoistureSensor):
    schedule_manager = ScheduleManager()
    # Get the worker interval from an environment variable, default to 15 seconds if not set
    worker_interval = int(os.getenv("HYDRO_WORKER_INTERVAL", 15))
    moisture_readings = []
    with open("moisture_log.txt", "r") as f:
        raw_readings = f.readlines()
        # Parse readings into (timestamp, moisture_level) tuples
        moisture_readings = []
        for line in raw_readings:
            try:
                timestamp_str, moisture_str = line.strip().split(", ")
                timestamp = datetime.datetime.fromisoformat(timestamp_str)
                moisture_level = int(moisture_str)
                moisture_readings.append((timestamp, moisture_level))
            except Exception as e:
                print(f"Error reading moisture log. Is it not formatted correctly?: Line '{line}': {e}")

    while True:
        print("=== Hydroponics Worker Event Loop ===")

        current_time = datetime.datetime.now()
        current_day = current_time.weekday()  # 0=Monday, 6=Sunday
        current_time_of_day = current_time.time()
        days = ["Mon","Tue","Wed","Thu","Fri", "Sat", "Sun"]
        print(f"Current time: {current_time}, Day: {days[current_day]}, Time of day: {current_time_of_day}")

        # Record the current moisture level into a log file
        moisture_level = await sensor.get_moisture_level()
        moisture_readings.append((current_time, moisture_level))
        with open("moisture_log.txt", "a") as f:
            f.write(f"{current_time.isoformat()}, {moisture_level}\n")
        
        print(moisture_history_string(moisture_readings, minutes=30))

        # Get all active schedules
        schedules = [s for s in schedule_manager.get_all() if s.active]
        print(f"Found {len(schedules)} active schedules.")

        for schedule in schedules:
            print(f"[Plant: {schedule.plant_name} - {schedule.id}]")
            daystring = ", ".join([days[d] for d in schedule.days_of_week])
            print(f"* Days: {daystring}")
            print(f"* Times: {[t.strftime('%H:%M') for t in schedule.schedule_times]}")
            should_water = False
            
            # Check time-based schedule
            if schedule.schedule_times and current_day in schedule.days_of_week:
                for scheduled_time in schedule.schedule_times:
                    time_diff = (
                        datetime.datetime.combine(datetime.date.min, current_time_of_day) - 
                        datetime.datetime.combine(datetime.date.min, scheduled_time)
                    )
                    # If we're within 1 minute of the scheduled time
                    if time_diff > 0 and time_diff.total_seconds() < 60:
                        print("* ⏲️ Reached scheduled time:", scheduled_time)
                        should_water = True
                        break
            
            # Check moisture-based schedule
            if schedule.moisture_threshold is not None:
                print(f"* Moisture Threshold: {schedule.moisture_threshold}%")
                moisture_level = await sensor.get_moisture_level()
                print(f"* Current Moisture Level: {moisture_level}%")
                if moisture_level < schedule.moisture_threshold:
                    # Check if we haven't watered recently (respect check_interval_minutes)
                    if (schedule.last_watered is None or 
                        (current_time - schedule.last_watered).total_seconds() > 
                        schedule.check_interval_minutes * 60):
                        should_water = True
                        print(f"* 🌵 Moisture below threshold.")
                    else:
                        print(f"* We watered < {schedule.check_interval_minutes}m ago. Skipping watering.")
            
            # Water if needed
            if should_water:
                print(f"* 💧💧💧 Watering plant! 💧💧💧")
                asyncio.create_task(pump.activate(schedule.pump_duration_seconds))
                schedule_manager.record_watering(schedule.id)
        
        # Sleep for a short time before checking again
        await asyncio.sleep(worker_interval)  # Check every 15 seconds
        
