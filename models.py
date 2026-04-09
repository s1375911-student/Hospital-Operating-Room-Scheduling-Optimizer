from abc import ABC
from datetime import datetime, timedelta


class Person(ABC):
    """Abstract base class for hospital personnel."""
    
    def __init__(self, person_id, name, contact_info):
        self.person_id = person_id
        self.name = name
        self.contact_info = contact_info


class Surgeon(Person):
    """Represents a surgeon with specialization and assigned surgeries."""
    
    def __init__(self, person_id, name, contact_info, specialization):
        super().__init__(person_id, name, contact_info)
        self.specialization = specialization
        self.assigned_surgeries = set()  # Use set for O(1) lookup and removal
    
    def add_surgery(self, surgery):
        self.assigned_surgeries.add(surgery)
    
    def remove_surgery(self, surgery):
        self.assigned_surgeries.discard(surgery)  # discard doesn't raise if not found


class Patient(Person):
    """Represents a patient with urgency score."""
    
    def __init__(self, person_id, name, contact_info, urgency_score):
        super().__init__(person_id, name, contact_info)
        if not 1 <= urgency_score <= 10:
            raise ValueError("Urgency score must be between 1 and 10")
        self.urgency_score = urgency_score


class TimeSlot:
    """Represents a time slot with validation."""
    
    HOSPITAL_START = 8  # 8 AM
    HOSPITAL_END = 18   # 6 PM
    
    def __init__(self, start_time, end_time):
        if start_time >= end_time:
            raise ValueError("Start time must be before end time")
        if start_time < self.HOSPITAL_START or end_time > self.HOSPITAL_END:
            raise ValueError(f"Time slot must be within {self.HOSPITAL_START}:00 to {self.HOSPITAL_END}:00")
        self.start_time = start_time
        self.end_time = end_time
    
    def duration(self):
        return self.end_time - self.start_time
    
    def overlaps(self, other):
        return self.start_time < other.end_time and other.start_time < self.end_time
    
    def __repr__(self):
        return f"TimeSlot({self.start_time}:00-{self.end_time}:00)"


class Surgery:
    """Represents a surgery with time interval and resource requirements."""
    
    def __init__(self, surgery_id, patient, surgeon, operating_room, time_slot):
        self.surgery_id = surgery_id
        self.patient = patient
        self.surgeon = surgeon
        self.operating_room = operating_room
        self.time_slot = time_slot
        self.scheduled = False
    
    def __repr__(self):
        return f"Surgery({self.surgery_id}, {self.patient.name}, {self.time_slot})"


class OperatingRoom:
    """Represents an operating room."""
    
    def __init__(self, room_id, room_type):
        self.room_id = room_id
        self.room_type = room_type
        self.scheduled_surgeries = []
    
    def add_surgery(self, surgery):
        self.scheduled_surgeries.append(surgery)
    
    def remove_surgery(self, surgery):
        if surgery in self.scheduled_surgeries:
            self.scheduled_surgeries.remove(surgery)
    
    def get_utilization(self):
        """Calculate utilization rate (0-1)."""
        if not self.scheduled_surgeries:
            return 0.0
        total_duration = sum(s.time_slot.duration() for s in self.scheduled_surgeries)
        max_hours = TimeSlot.HOSPITAL_END - TimeSlot.HOSPITAL_START
        return min(total_duration / max_hours, 1.0)
