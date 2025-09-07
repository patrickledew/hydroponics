from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any
from datetime import datetime, time
import json
import uuid

@dataclass
class Schedule:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    plant_name: str = ""
    active: bool = True
    
    # Time-based scheduling
    schedule_times: List[time] = field(default_factory=list)  # List of times to water each day
    days_of_week: List[int] = field(default_factory=lambda: list(range(7)))  # 0=Monday, 6=Sunday
    
    # Moisture-based scheduling
    moisture_threshold: Optional[int] = None  # Water when moisture falls below this level (%)
    check_interval_minutes: int = 30  # How often to check moisture levels
    
    # Watering parameters
    pump_duration_seconds: int = 5  # How long to run the pump
    
    # Last watered timestamp
    last_watered: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Convert time objects to strings
        data['schedule_times'] = [t.strftime('%H:%M') for t in self.schedule_times]
        data['last_watered'] = self.last_watered.isoformat() if self.last_watered else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        # Convert time strings back to time objects
        if 'schedule_times' in data:
            data['schedule_times'] = [
                datetime.strptime(t, '%H:%M').time() 
                for t in data['schedule_times']
            ]
        if 'last_watered' in data and data['last_watered']:
            data['last_watered'] = datetime.fromisoformat(data['last_watered'])
        return cls(**data)
