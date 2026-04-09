"""
sample_data.py - Shared sample data factory and CSV import/export utilities.

Provides create_sample_data() used by both CLI and GUI to avoid duplication.
Includes a conflicting dataset that produces visibly different results across
the three scheduling algorithms. Also provides CSV import/export for real data.
"""

import csv
import os
import logging
from models import Surgeon, Patient, Surgery, TimeSlot, OperatingRoom
from hospital_manager import Hospital

logger = logging.getLogger(__name__)


def create_sample_data():
    """Initialize sample hospital data with intentional conflicts.

    This dataset is designed so the three schedulers produce DIFFERENT results:
    - Several surgeries compete for the same room and time slot.
    - Surgeon availability creates additional contention.
    - Urgency scores vary so Priority scheduler picks differently from Greedy.

    Returns:
        (Hospital, list[Surgery])
    """
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

    surgeries = []

    # --- CONFLICTING DATASET ---
    # Surgeries are designed with overlapping times in the same rooms and
    # shared surgeons so the algorithms MUST make different trade-offs.

    configs = [
        # (surgery_id, patient_name, urgency, surgeon, room, start, end)
        # OR001 block: 3 surgeries compete for 8-12 window
        ("SUR000", "P001", "John Doe",    9, surgeon1, or1,  8, 10),
        ("SUR001", "P002", "Jane Smith",  4, surgeon1, or1,  9, 12),  # overlaps SUR000
        ("SUR002", "P003", "Bob Johnson", 8, surgeon1, or1, 10, 12),

        # OR002 block: surgeon2 is double-booked across rooms
        ("SUR003", "P004", "Alice Brown",   6, surgeon2, or2, 8, 11),
        ("SUR004", "P005", "Charlie Davis", 10, surgeon2, or3, 9, 11), # surgeon conflict w/ SUR003

        # OR002 afternoon: competing surgeries
        ("SUR005", "P006", "Diana Wilson",   3, surgeon2, or2, 11, 14),
        ("SUR006", "P007", "Eve Martinez",   9, surgeon2, or2, 12, 15), # overlaps SUR005

        # OR003: surgeon3 double-booked
        ("SUR007", "P008", "Frank Garcia",   7, surgeon3, or3,  8, 10),
        ("SUR008", "P009", "Grace Lee",      5, surgeon3, or3,  9, 11), # overlaps SUR007
        ("SUR009", "P010", "Hank Brown",     8, surgeon3, or3, 11, 13),

        # Late afternoon — no conflicts (baseline)
        ("SUR010", "P011", "Ivy Chen",       6, surgeon1, or1, 14, 16),
        ("SUR011", "P012", "Jack White",     7, surgeon3, or3, 14, 16),
    ]

    for (sur_id, pat_id, name, urgency, surgeon, room, start, end) in configs:
        patient = Patient(pat_id, name, f"{name.lower().replace(' ', '')}@email.com", urgency)
        time_slot = TimeSlot(start, end)
        surgery = Surgery(sur_id, patient, surgeon, room, time_slot)
        surgeries.append(surgery)

    logger.info(f"Created sample data: {len(surgeries)} surgeries with intentional conflicts")
    return hospital, surgeries


def create_scalability_data(num_surgeries, num_rooms=5, num_surgeons=4):
    """Create larger datasets for scalability testing.

    Distributes surgeries across rooms and surgeons with realistic overlap
    patterns so algorithms produce meaningfully different results at scale.

    Args:
        num_surgeries: total surgeries to create.
        num_rooms: number of operating rooms.
        num_surgeons: number of surgeons.

    Returns:
        (Hospital, list[Surgery])
    """
    hospital = Hospital("H_SCALE", "Scalability Test Hospital")

    rooms = []
    for i in range(num_rooms):
        room = OperatingRoom(f"OR{i:03d}", "General")
        hospital.add_operating_room(room)
        rooms.append(room)

    surgeons = [
        Surgeon(f"S{i:03d}", f"Dr. Surgeon{i}", f"dr{i}@test.com", "General")
        for i in range(num_surgeons)
    ]

    surgeries = []
    for i in range(num_surgeries):
        urgency = (i % 10) + 1
        patient = Patient(f"P{i:04d}", f"Patient {i}", f"p{i}@test.com", urgency)
        surgeon = surgeons[i % num_surgeons]
        room = rooms[i % num_rooms]
        # Create overlapping 2-hour blocks that cycle through the day
        start = 8 + (i % 5) * 2  # 8, 10, 12, 14, 16
        end = min(start + 2, 18)
        if start >= 18:
            start, end = 8, 10
        time_slot = TimeSlot(start, end)
        surgery = Surgery(f"SUR{i:04d}", patient, surgeon, room, time_slot)
        surgeries.append(surgery)

    return hospital, surgeries


# ---- CSV Import / Export ----

def export_schedule_to_csv(scheduled_surgeries, filepath):
    """Export a list of scheduled surgeries to a CSV file.

    Args:
        scheduled_surgeries: list of Surgery objects.
        filepath: output CSV path.
    """
    try:
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "surgery_id", "patient_id", "patient_name", "urgency",
                "surgeon_id", "surgeon_name", "room_id",
                "start_time", "end_time",
            ])
            for s in scheduled_surgeries:
                writer.writerow([
                    s.surgery_id, s.patient.person_id, s.patient.name,
                    s.patient.urgency_score, s.surgeon.person_id,
                    s.surgeon.name, s.operating_room.room_id,
                    s.time_slot.start_time, s.time_slot.end_time,
                ])
        logger.info(f"Exported {len(scheduled_surgeries)} surgeries to {filepath}")
    except IOError as e:
        logger.error(f"Failed to export CSV: {e}")
        raise


def import_surgeries_from_csv(filepath, hospital):
    """Import surgeries from a CSV file.

    CSV columns: surgery_id, patient_id, patient_name, urgency,
                 surgeon_id, surgeon_name, room_id, start_time, end_time

    Surgeons and rooms are matched by ID from the hospital or created on the fly.

    Args:
        filepath: input CSV path.
        hospital: Hospital instance (rooms must already exist).

    Returns:
        list[Surgery]
    """
    surgeons_cache = {}
    room_map = {r.room_id: r for r in hospital.operating_rooms}
    surgeries = []

    try:
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get or create surgeon
                surgeon_id = row["surgeon_id"]
                if surgeon_id not in surgeons_cache:
                    surgeons_cache[surgeon_id] = Surgeon(
                        surgeon_id, row["surgeon_name"],
                        f"{surgeon_id}@hospital.com", "General"
                    )
                surgeon = surgeons_cache[surgeon_id]

                # Get room
                room_id = row["room_id"]
                if room_id not in room_map:
                    logger.warning(f"Room {room_id} not in hospital, creating it")
                    room = OperatingRoom(room_id, "Imported")
                    hospital.add_operating_room(room)
                    room_map[room_id] = room
                room = room_map[room_id]

                patient = Patient(
                    row["patient_id"], row["patient_name"],
                    f"{row['patient_id']}@email.com", int(row["urgency"])
                )
                time_slot = TimeSlot(int(row["start_time"]), int(row["end_time"]))
                surgery = Surgery(row["surgery_id"], patient, surgeon, room, time_slot)
                surgeries.append(surgery)

        logger.info(f"Imported {len(surgeries)} surgeries from {filepath}")
        return surgeries

    except (IOError, KeyError, ValueError) as e:
        logger.error(f"Failed to import CSV: {e}")
        raise
