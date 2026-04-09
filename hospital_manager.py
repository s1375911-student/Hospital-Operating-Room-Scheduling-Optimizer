from interval_tree import IntervalTree
from models import TimeSlot


class Hospital:
    """Central hub managing operating rooms and scheduling."""
    
    def __init__(self, hospital_id, name):
        self.hospital_id = hospital_id
        self.name = name
        self.operating_rooms = []
        self.scheduled_surgeries = []
        self.interval_tree = IntervalTree()
        self.conflict_count = 0
    
    def add_operating_room(self, operating_room):
        """Add an operating room to the hospital."""
        self.operating_rooms.append(operating_room)
    
    def add_surgery(self, surgery):
        """Add a surgery to the schedule.
        
        Returns True if successful, False if conflict detected.
        """
        # Prevent duplicate surgeries
        if surgery in self.scheduled_surgeries:
            return False
        
        interval = (surgery.time_slot.start_time, surgery.time_slot.end_time)
        
        # Check for conflicts in same operating room only
        for scheduled in self.scheduled_surgeries:
            if (scheduled.operating_room == surgery.operating_room and
                scheduled.time_slot.overlaps(surgery.time_slot)):
                self.conflict_count += 1
                return False
        
        self.scheduled_surgeries.append(surgery)
        surgery.operating_room.add_surgery(surgery)
        surgery.surgeon.add_surgery(surgery)
        self.interval_tree.insert(interval)
        surgery.scheduled = True
        return True
    
    def cancel_surgery(self, surgery):
        """Cancel a scheduled surgery."""
        if surgery in self.scheduled_surgeries:
            self.scheduled_surgeries.remove(surgery)
            surgery.operating_room.remove_surgery(surgery)
            surgery.surgeon.remove_surgery(surgery)
            interval = (surgery.time_slot.start_time, surgery.time_slot.end_time)
            self.interval_tree.delete(interval)
            surgery.scheduled = False
            return True
        return False
    
    def generate_utilization_report(self):
        """Generate comprehensive performance metrics."""
        if not self.operating_rooms:
            return {}
        
        total_utilization = sum(room.get_utilization() for room in self.operating_rooms)
        avg_utilization = total_utilization / len(self.operating_rooms)
        
        avg_urgency_score = (sum(surgery.patient.urgency_score 
                                   for surgery in self.scheduled_surgeries) / len(self.scheduled_surgeries)
                            if self.scheduled_surgeries else 0)
        
        return {
            'total_surgeries_scheduled': len(self.scheduled_surgeries),
            'total_operating_rooms': len(self.operating_rooms),
            'average_utilization': avg_utilization,
            'average_urgency_score': avg_urgency_score,
            'conflict_count': self.conflict_count,
            'room_details': [
                {
                    'room_id': room.room_id,
                    'room_type': room.room_type,
                    'surgeries_scheduled': len(room.scheduled_surgeries),
                    'utilization': room.get_utilization()
                }
                for room in self.operating_rooms
            ]
        }
