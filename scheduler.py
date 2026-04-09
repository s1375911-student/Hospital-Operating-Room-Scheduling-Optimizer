from abc import ABC, abstractmethod
import heapq
import time


class Scheduler(ABC):
    """Abstract base class for scheduling strategies."""
    
    def __init__(self, hospital):
        self.hospital = hospital
        self.runtime = 0
    
    @abstractmethod
    def run_schedule(self, surgeries):
        """Schedule surgeries according to strategy.
        
        Returns list of successfully scheduled surgeries.
        """
        pass


class GreedyScheduler(Scheduler):
    """Greedy scheduler using Earliest Finish Time strategy.
    
    Sorts surgeries by finish time to maximize number of surgeries per room.
    Time Complexity: O(n log n) for sorting + O(n log n) for interval tree operations
    """
    
    def run_schedule(self, surgeries):
        start_time = time.time()
        scheduled = []
        
        # Sort by finish time (earliest finish first)
        sorted_surgeries = sorted(surgeries, key=lambda s: s.time_slot.end_time)
        
        for surgery in sorted_surgeries:
            if self._can_schedule(surgery):
                self.hospital.add_surgery(surgery)
                scheduled.append(surgery)
        
        self.runtime = time.time() - start_time
        return scheduled
    
    def _can_schedule(self, surgery):
        """Check if surgery can be scheduled without conflicts."""
        interval = (surgery.time_slot.start_time, surgery.time_slot.end_time)
        overlaps = self.hospital.interval_tree.search_overlap(interval)
        
        # Filter overlaps to same operating room
        room_conflicts = [s for s in self.hospital.scheduled_surgeries 
                         if s.operating_room == surgery.operating_room 
                         and (s.time_slot.start_time, s.time_slot.end_time) in overlaps]
        
        return len(room_conflicts) == 0


class PriorityScheduler(Scheduler):
    """Priority-based scheduler using heap for patient urgency.
    
    Prioritizes patients with higher urgency scores.
    Time Complexity: O(n log n) for heap operations + O(n log n) for interval tree
    """
    
    def run_schedule(self, surgeries):
        start_time = time.time()
        scheduled = []
        
        # Create max heap (negate urgency for min heap)
        heap = [(-s.patient.urgency_score, i, s) for i, s in enumerate(surgeries)]
        heapq.heapify(heap)
        
        while heap:
            _, _, surgery = heapq.heappop(heap)
            if self._can_schedule(surgery):
                self.hospital.add_surgery(surgery)
                scheduled.append(surgery)
        
        self.runtime = time.time() - start_time
        return scheduled
    
    def _can_schedule(self, surgery):
        """Check if surgery can be scheduled without conflicts."""
        interval = (surgery.time_slot.start_time, surgery.time_slot.end_time)
        overlaps = self.hospital.interval_tree.search_overlap(interval)
        
        room_conflicts = [s for s in self.hospital.scheduled_surgeries 
                         if s.operating_room == surgery.operating_room 
                         and (s.time_slot.start_time, s.time_slot.end_time) in overlaps]
        
        return len(room_conflicts) == 0


class OptimizedScheduler(Scheduler):
    """Branch-and-Bound optimizer for minimum idle time.
    
    Finds schedule with absolute minimum idle time in operating rooms.
    Time Complexity: O(2^n) worst case, but pruned significantly in practice
    """
    
    def run_schedule(self, surgeries):
        start_time = time.time()
        
        # Sort by duration (longest first) for better pruning
        sorted_surgeries = sorted(surgeries, key=lambda s: s.time_slot.duration(), reverse=True)
        
        best = [float('inf'), []]
        
        self._branch_and_bound(sorted_surgeries, [], best)
        
        for surgery in best[1]:
            self.hospital.add_surgery(surgery)
        
        self.runtime = time.time() - start_time
        return best[1]
    
    def _branch_and_bound(self, remaining, current, best):
        """Recursively explore scheduling possibilities with pruning."""
        idle = self._calculate_idle_time(current)
        
        # Prune: current idle time already exceeds best found
        if idle >= best[0] and remaining:
            return
        
        if not remaining:
            if idle < best[0]:
                best[0] = idle
                best[1] = list(current)
            return
        
        surgery = remaining[0]
        
        # Try scheduling this surgery
        if self._can_schedule_temp(surgery, current):
            current.append(surgery)
            self._branch_and_bound(remaining[1:], current, best)
            current.pop()
        
        # Try skipping this surgery
        self._branch_and_bound(remaining[1:], current, best)
    
    def _can_schedule_temp(self, surgery, current_schedule):
        """Check if surgery conflicts with current schedule (room and surgeon)."""
        for scheduled in current_schedule:
            if scheduled.time_slot.overlaps(surgery.time_slot):
                if (scheduled.operating_room == surgery.operating_room or
                        scheduled.surgeon == surgery.surgeon):
                    return False
        return True
    
    def _calculate_idle_time(self, schedule):
        """Calculate total idle time across all hospital rooms."""
        from models import TimeSlot
        max_hours = TimeSlot.HOSPITAL_END - TimeSlot.HOSPITAL_START
        
        room_usage = {room.room_id: 0 for room in self.hospital.operating_rooms}
        for surgery in schedule:
            room_usage[surgery.operating_room.room_id] += surgery.time_slot.duration()
        
        return sum(max_hours - used for used in room_usage.values())
