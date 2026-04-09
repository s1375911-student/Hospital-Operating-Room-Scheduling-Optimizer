from models import Surgeon, Patient, Surgery, TimeSlot, OperatingRoom
from hospital_manager import Hospital
from scheduler import GreedyScheduler, PriorityScheduler, OptimizedScheduler
from interval_tree import IntervalTree


def create_sample_data():
    """Initialize sample hospital data."""
    hospital = Hospital("H001", "Metropolitan Hospital")
    
    # Create operating rooms
    or1 = OperatingRoom("OR001", "General Surgery")
    or2 = OperatingRoom("OR002", "Cardiology")
    or3 = OperatingRoom("OR003", "Orthopedics")
    
    hospital.add_operating_room(or1)
    hospital.add_operating_room(or2)
    hospital.add_operating_room(or3)
    
    # Create surgeons
    surgeon1 = Surgeon("S001", "Dr. Smith", "smith@hospital.com", "General Surgery")
    surgeon2 = Surgeon("S002", "Dr. Johnson", "johnson@hospital.com", "Cardiology")
    surgeon3 = Surgeon("S003", "Dr. Williams", "williams@hospital.com", "Orthopedics")
    
    # Create patients and surgeries
    surgeries = []
    
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
        (0, surgeon1, or1, 8, 10),   # General Surgery
        (1, surgeon1, or1, 10, 12),
        (2, surgeon2, or2, 9, 11),   # Cardiology
        (3, surgeon2, or2, 11, 13),
        (4, surgeon3, or3, 8, 10),   # Orthopedics
        (5, surgeon3, or3, 10, 12),
        (6, surgeon1, or1, 13, 15),
        (7, surgeon2, or2, 14, 16),
    ]
    
    for idx, (patient_id, name, contact, urgency) in enumerate(patients_data):
        patient = Patient(patient_id, name, contact, urgency)
        surgeon, room, start, end = (surgery_configs[idx][1], surgery_configs[idx][2],
                                     surgery_configs[idx][3], surgery_configs[idx][4])
        time_slot = TimeSlot(start, end)
        surgery = Surgery(f"SUR{idx:03d}", patient, surgeon, room, time_slot)
        surgeries.append(surgery)
    
    return hospital, surgeries


def run_simulation(hospital, surgeries, scheduler_class, scheduler_name):
    """Run scheduling simulation with given scheduler."""
    print(f"\n{'='*60}")
    print(f"Running {scheduler_name}")
    print(f"{'='*60}")
    
    # Reset hospital state
    hospital.scheduled_surgeries = []
    hospital.interval_tree = IntervalTree()
    hospital.conflict_count = 0
    for room in hospital.operating_rooms:
        room.scheduled_surgeries = []
    
    scheduler = scheduler_class(hospital)
    scheduled = scheduler.run_schedule(surgeries)
    
    print(f"Surgeries scheduled: {len(scheduled)}/{len(surgeries)}")
    print(f"Algorithm runtime: {scheduler.runtime:.6f} seconds")
    print(f"Conflicts detected: {hospital.conflict_count}")
    
    return scheduled, scheduler.runtime


def display_results(hospital, scheduled_surgeries):
    """Display scheduling results and metrics."""
    report = hospital.generate_utilization_report()
    
    print(f"\nScheduled Surgeries:")
    for surgery in scheduled_surgeries:
        print(f"  {surgery.surgery_id}: {surgery.patient.name} - "
              f"{surgery.surgeon.name} - {surgery.operating_room.room_id} - "
              f"{surgery.time_slot}")
    
    print(f"\nPerformance Metrics:")
    print(f"  Total Surgeries Scheduled: {report['total_surgeries_scheduled']}")
    print(f"  Operating Rooms: {report['total_operating_rooms']}")
    print(f"  Average Utilization: {report['average_utilization']:.2%}")
    print(f"  Average Urgency Score: {report['average_urgency_score']:.2f}")
    print(f"  Conflicts Detected: {report['conflict_count']}")
    
    print(f"\nRoom Details:")
    for room in report['room_details']:
        print(f"  {room['room_id']} ({room['room_type']}): "
              f"{room['surgeries_scheduled']} surgeries, "
              f"Utilization: {room['utilization']:.2%}")


def scalability_test():
    """Test system scalability with increasing dataset sizes."""
    print(f"\n{'='*60}")
    print("SCALABILITY TEST")
    print(f"{'='*60}")
    
    test_sizes = [10, 20, 50]
    
    for size in test_sizes:
        print(f"\nTesting with {size} surgeries...")
        hospital = Hospital("H_TEST", "Test Hospital")
        
        # Create rooms
        for i in range(3):
            hospital.add_operating_room(OperatingRoom(f"OR{i}", "General"))
        
        # Create surgeons
        surgeons = [Surgeon(f"S{i}", f"Dr. {i}", f"dr{i}@test.com", "General") 
                   for i in range(2)]
        
        # Create surgeries
        surgeries = []
        for i in range(size):
            patient = Patient(f"P{i}", f"Patient {i}", f"p{i}@test.com", (i % 10) + 1)
            surgeon = surgeons[i % len(surgeons)]
            room = hospital.operating_rooms[i % len(hospital.operating_rooms)]
            start = 8 + (i % 8)
            end = min(start + 2, 18)
            time_slot = TimeSlot(start, end)
            surgery = Surgery(f"SUR{i}", patient, surgeon, room, time_slot)
            surgeries.append(surgery)
        
        # Test each scheduler
        for scheduler_class, name in [(GreedyScheduler, "Greedy"),
                                      (PriorityScheduler, "Priority"),
                                      (OptimizedScheduler, "Optimized")]:
            _, runtime = run_simulation(hospital, surgeries, scheduler_class, name)
            print(f"  {name}: {runtime:.6f}s")


def run_cli():
    """Main CLI execution function."""
    print("Hospital Operating Room Scheduling Optimizer")
    print("=" * 60)
    
    # Create sample data
    hospital, surgeries = create_sample_data()
    
    # Run simulations with different schedulers
    schedulers = [
        (GreedyScheduler, "Greedy Scheduler (Earliest Finish Time)"),
        (PriorityScheduler, "Priority Scheduler (Patient Urgency)"),
        (OptimizedScheduler, "Optimized Scheduler (Branch-and-Bound)")
    ]
    
    results = {}
    for scheduler_class, scheduler_name in schedulers:
        scheduled, runtime = run_simulation(hospital, surgeries, scheduler_class, scheduler_name)
        results[scheduler_name] = {
            'scheduled': len(scheduled),
            'runtime': runtime,
            'conflicts': hospital.conflict_count
        }
        display_results(hospital, scheduled)
    
    # Comparison summary
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")
    for name, metrics in results.items():
        print(f"\n{name}:")
        print(f"  Surgeries Scheduled: {metrics['scheduled']}")
        print(f"  Runtime: {metrics['runtime']:.6f}s")
        print(f"  Conflicts: {metrics['conflicts']}")
    
    # Scalability test
    scalability_test()


if __name__ == "__main__":
    run_cli()
