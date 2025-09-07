import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import threading
from schedule import Schedule

class ScheduleManager:
    def __init__(self, storage_file: str = "schedules.json"):
        self.storage_file = storage_file
        self.schedules: Dict[str, Schedule] = {}
        self.lock = threading.Lock()
        self._load_schedules()
    
    def _load_schedules(self) -> None:
        """Load schedules from storage file"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    schedule = Schedule.from_dict(item)
                    self.schedules[schedule.id] = schedule
    
    def _save_schedules(self) -> None:
        """Save schedules to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump([s.to_dict() for s in self.schedules.values()], f, indent=2)
    
    def get_all(self) -> List[Schedule]:
        """Get all schedules"""
        with self.lock:
            return list(self.schedules.values())
    
    def get(self, schedule_id: str) -> Optional[Schedule]:
        """Get a specific schedule by ID"""
        with self.lock:
            return self.schedules.get(schedule_id)
    
    def create(self, schedule_data: Dict[str, Any]) -> Schedule:
        """Create a new schedule"""
        schedule = Schedule.from_dict(schedule_data)
        with self.lock:
            self.schedules[schedule.id] = schedule
            self._save_schedules()
        return schedule
    
    def update(self, schedule_id: str, schedule_data: Dict[str, Any]) -> Optional[Schedule]:
        """Update an existing schedule"""
        with self.lock:
            if schedule_id not in self.schedules:
                return None
            
            # Keep the same ID
            schedule_data['id'] = schedule_id
            schedule = Schedule.from_dict(schedule_data)
            self.schedules[schedule_id] = schedule
            self._save_schedules()
            return schedule
    
    def delete(self, schedule_id: str) -> bool:
        """Delete a schedule"""
        with self.lock:
            if schedule_id not in self.schedules:
                return False
            del self.schedules[schedule_id]
            self._save_schedules()
            return True
    
    def activate(self, schedule_id: str) -> bool:
        """Activate a schedule"""
        with self.lock:
            if schedule_id not in self.schedules:
                return False
            self.schedules[schedule_id].active = True
            self._save_schedules()
            return True
    
    def deactivate(self, schedule_id: str) -> bool:
        """Deactivate a schedule"""
        with self.lock:
            if schedule_id not in self.schedules:
                return False
            self.schedules[schedule_id].active = False
            self._save_schedules()
            return True
    
    def record_watering(self, schedule_id: str) -> bool:
        """Record that watering occurred for a schedule"""
        with self.lock:
            if schedule_id not in self.schedules:
                return False
            self.schedules[schedule_id].last_watered = datetime.now()
            self._save_schedules()
            return True
