import tkinter as tk
from tkinter import ttk, messagebox
from models import Surgeon, Patient, Surgery, TimeSlot, OperatingRoom
from hospital_manager import Hospital
from scheduler import GreedyScheduler, PriorityScheduler, OptimizedScheduler
import threading
import queue


class HospitalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital OR Scheduling Optimizer")
        self.root.geometry("1000x700")
        self.hospital = None
        self.surgeries = []
        self.results = {}
        self.results_lock = threading.Lock()  # Thread-safe results access
        self.result_queue = queue.Queue()  # Queue for thread communication
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main UI layout."""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(header, text="Hospital OR Scheduling Optimizer", 
                 font=("Arial", 16, "bold")).pack()
        
        # Main content area
        content = ttk.Frame(self.root)
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = ttk.LabelFrame(content, text="Controls", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        ttk.Button(left_panel, text="Initialize Hospital", 
                  command=self.initialize_hospital).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Run Greedy Scheduler", 
                  command=lambda: self.run_scheduler(GreedyScheduler, "Greedy")).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Run Priority Scheduler", 
                  command=lambda: self.run_scheduler(PriorityScheduler, "Priority")).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Run Optimized Scheduler", 
                  command=lambda: self.run_scheduler(OptimizedScheduler, "Optimized")).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Compare All", 
                  command=self.compare_all).pack(fill=tk.X, pady=5)
        ttk.Button(left_panel, text="Clear Results", 
                  command=self.clear_results).pack(fill=tk.X, pady=5)
        
        # Right panel - Results
        right_panel = ttk.LabelFrame(content, text="Results", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Metrics tab
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="Metrics")
        self.metrics_text = tk.Text(metrics_frame, height=20, width=50, state=tk.DISABLED)
        self.metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Schedule tab
        schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(schedule_frame, text="Schedule")
        self.schedule_text = tk.Text(schedule_frame, height=20, width=50, state=tk.DISABLED)
        self.schedule_text.pack(fill=tk.BOTH, expand=True)
        
        # Comparison tab
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Comparison")
        self.comparison_text = tk.Text(comparison_frame, height=20, width=50, state=tk.DISABLED)
        self.comparison_text.pack(fill=tk.BOTH, expand=True)
    
    def initialize_hospital(self):
        """Initialize hospital with sample data."""
        self.hospital = Hospital("H001", "Metropolitan Hospital")
        
        # Create operating rooms
        for i, room_type in enumerate(["General Surgery", "Cardiology", "Orthopedics"]):
            self.hospital.add_operating_room(OperatingRoom(f"OR{i+1:03d}", room_type))
        
        # Create surgeons
        surgeons = [
            Surgeon("S001", "Dr. Smith", "smith@hospital.com", "General Surgery"),
            Surgeon("S002", "Dr. Johnson", "johnson@hospital.com", "Cardiology"),
            Surgeon("S003", "Dr. Williams", "williams@hospital.com", "Orthopedics")
        ]
        
        # Create surgeries
        self.surgeries = []
        patients_data = [
            ("P001", "John Doe", "john@email.com", 9),
            ("P002", "Jane Smith", "jane@email.com", 7),
            ("P003", "Bob Johnson", "bob@email.com", 8),
            ("P004", "Alice Brown", "alice@email.com", 6),
            ("P005", "Charlie Davis", "charlie@email.com", 9),
            ("P006", "Diana Wilson", "diana@email.com", 5),
            ("P007", "Eve Martinez", "eve@email.com", 8),
            ("P008", "Frank Garcia", "frank@email.com", 7),
        ]
        
        surgery_configs = [
            (surgeons[0], self.hospital.operating_rooms[0], 8, 10),
            (surgeons[0], self.hospital.operating_rooms[0], 10, 12),
            (surgeons[1], self.hospital.operating_rooms[1], 9, 11),
            (surgeons[1], self.hospital.operating_rooms[1], 11, 13),
            (surgeons[2], self.hospital.operating_rooms[2], 8, 10),
            (surgeons[2], self.hospital.operating_rooms[2], 10, 12),
            (surgeons[0], self.hospital.operating_rooms[0], 13, 15),
            (surgeons[1], self.hospital.operating_rooms[1], 14, 16),
        ]
        
        for idx, (patient_id, name, contact, urgency) in enumerate(patients_data):
            patient = Patient(patient_id, name, contact, urgency)
            surgeon, room, start, end = surgery_configs[idx]
            time_slot = TimeSlot(start, end)
            surgery = Surgery(f"SUR{idx:03d}", patient, surgeon, room, time_slot)
            self.surgeries.append(surgery)
        
        messagebox.showinfo("Success", f"Hospital initialized with {len(self.surgeries)} surgeries")
        self.update_metrics_display()
    
    def run_scheduler(self, scheduler_class, name):
        """Run a scheduler in a separate thread."""
        if not self.hospital:
            messagebox.showerror("Error", "Please initialize hospital first")
            return
        
        def run():
            self.reset_hospital()
            scheduler = scheduler_class(self.hospital)
            scheduled = scheduler.run_schedule(self.surgeries)
            
            # Use lock for thread-safe dictionary access
            with self.results_lock:
                self.results[name] = {
                    'scheduled': len(scheduled),
                    'runtime': scheduler.runtime,
                    'conflicts': self.hospital.conflict_count,
                    'surgeries': scheduled
                }
            
            self.root.after(0, lambda: self.display_results(name, scheduled))
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def compare_all(self):
        """Compare all schedulers."""
        if not self.hospital:
            messagebox.showerror("Error", "Please initialize hospital first")
            return
        
        def run():
            for scheduler_class, name in [(GreedyScheduler, "Greedy"),
                                         (PriorityScheduler, "Priority"),
                                         (OptimizedScheduler, "Optimized")]:
                self.reset_hospital()
                scheduler = scheduler_class(self.hospital)
                scheduled = scheduler.run_schedule(self.surgeries)
                
                # Use lock for thread-safe dictionary access
                with self.results_lock:
                    self.results[name] = {
                        'scheduled': len(scheduled),
                        'runtime': scheduler.runtime,
                        'conflicts': self.hospital.conflict_count,
                        'surgeries': scheduled
                    }
            
            self.root.after(0, self.display_comparison)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def reset_hospital(self):
        """Reset hospital state for new scheduling."""
        from interval_tree import IntervalTree
        self.hospital.scheduled_surgeries = []
        self.hospital.interval_tree = IntervalTree()
        self.hospital.conflict_count = 0
        for room in self.hospital.operating_rooms:
            room.scheduled_surgeries = []
    
    def display_results(self, scheduler_name, scheduled):
        """Display results for a single scheduler."""
        report = self.hospital.generate_utilization_report()
        
        # Update metrics
        metrics = f"Scheduler: {scheduler_name}\n"
        metrics += f"{'='*40}\n"
        metrics += f"Surgeries Scheduled: {report['total_surgeries_scheduled']}/{len(self.surgeries)}\n"
        metrics += f"Operating Rooms: {report['total_operating_rooms']}\n"
        metrics += f"Average Utilization: {report['average_utilization']:.2%}\n"
        metrics += f"Average Urgency Score: {report['average_urgency_score']:.2f}\n"
        metrics += f"Conflicts Detected: {report['conflict_count']}\n"
        metrics += f"Runtime: {self.results[scheduler_name]['runtime']:.6f}s\n\n"
        metrics += "Room Details:\n"
        for room in report['room_details']:
            metrics += f"  {room['room_id']} ({room['room_type']}): "
            metrics += f"{room['surgeries_scheduled']} surgeries, "
            metrics += f"Utilization: {room['utilization']:.2%}\n"
        
        self.update_text_widget(self.metrics_text, metrics)
        
        # Update schedule
        schedule = f"Scheduled Surgeries ({len(scheduled)}):\n"
        schedule += f"{'='*40}\n"
        for surgery in scheduled:
            schedule += f"{surgery.surgery_id}: {surgery.patient.name}\n"
            schedule += f"  Surgeon: {surgery.surgeon.name}\n"
            schedule += f"  Room: {surgery.operating_room.room_id}\n"
            schedule += f"  Time: {surgery.time_slot}\n\n"
        
        self.update_text_widget(self.schedule_text, schedule)
    
    def display_comparison(self):
        """Display comparison of all schedulers."""
        comparison = "Scheduler Comparison\n"
        comparison += f"{'='*50}\n\n"
        
        # Use lock for thread-safe dictionary read
        with self.results_lock:
            for name, metrics in self.results.items():
                comparison += f"{name} Scheduler:\n"
                comparison += f"  Surgeries Scheduled: {metrics['scheduled']}/{len(self.surgeries)}\n"
                comparison += f"  Runtime: {metrics['runtime']:.6f}s\n"
                comparison += f"  Conflicts: {metrics['conflicts']}\n\n"
        
        self.update_text_widget(self.comparison_text, comparison)
    
    def update_metrics_display(self):
        """Update metrics display with hospital info."""
        info = "Hospital Information\n"
        info += f"{'='*40}\n"
        info += f"Hospital: {self.hospital.name}\n"
        info += f"Operating Rooms: {len(self.hospital.operating_rooms)}\n"
        info += f"Total Surgeries: {len(self.surgeries)}\n\n"
        info += "Surgeries to Schedule:\n"
        for surgery in self.surgeries:
            info += f"  {surgery.surgery_id}: {surgery.patient.name} "
            info += f"(Urgency: {surgery.patient.urgency_score})\n"
        
        self.update_text_widget(self.metrics_text, info)
    
    def update_text_widget(self, widget, text):
        """Update text widget content."""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, text)
        widget.config(state=tk.DISABLED)
    
    def clear_results(self):
        """Clear all results."""
        self.results = {}
        self.update_text_widget(self.metrics_text, "")
        self.update_text_widget(self.schedule_text, "")
        self.update_text_widget(self.comparison_text, "")


def main():
    root = tk.Tk()
    gui = HospitalGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
