# Worker process for handling long-running tasks, including checking moisture levels and activating the pump.
import asyncio
import threading
import datetime
import time

from motor import MotorDriver
from sensor import MoistureSensor
from schedule_manager import ScheduleManager
import os


async def worker(pump: MotorDriver, sensor: MoistureSensor):
    schedule_manager = ScheduleManager()
    # Get the worker interval from an environment variable, default to 15 seconds if not set
    worker_interval = int(os.getenv("HYDRO_WORKER_INTERVAL", 15))
    
    while True:
        print("=== Hydroponics Worker Event Loop ===")

        current_time = datetime.datetime.now()
        current_day = current_time.weekday()  # 0=Monday, 6=Sunday
        current_time_of_day = current_time.time()
        days = ["Mon","Tue","Wed","Thu","Fri", "Sat", "Sun"]
        print(f"Current time: {current_time}, Day: {days[current_day]}, Time of day: {current_time_of_day}")
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
                    if abs(time_diff.total_seconds()) < 60:
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
                print(f"* 💧 Watering plant: {schedule.plant_name}")
                await pump.activate(schedule.pump_duration_seconds)
                schedule_manager.record_watering(schedule.id)
        
        # Sleep for a short time before checking again
        await asyncio.sleep(worker_interval)  # Check every 15 seconds
        
