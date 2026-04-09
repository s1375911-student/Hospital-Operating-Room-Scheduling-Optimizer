# Hospital Operating Room Scheduling Optimizer

An intelligent system for optimizing hospital operating room scheduling using multiple algorithmic strategies and advanced data structures.

## Overview

This project solves the complex real-world problem of scheduling surgeries across multiple operating rooms while considering:
- **Surgeon availability** - preventing double-booking
- **Patient urgency** - prioritizing critical cases
- **Room utilization** - maximizing efficiency
- **Conflict detection** - using Interval Tree for O(log n) performance

The system compares three distinct scheduling algorithms to find optimal solutions for different optimization goals.

## Key Features

### 🧮 Three Scheduling Algorithms
- **Greedy Scheduler** - Earliest Finish Time strategy for maximum throughput
- **Priority Scheduler** - Urgency-based heap for patient safety
- **Optimized Scheduler** - Branch-and-bound for minimum idle time

### 🌲 Advanced Data Structures
- **Interval Tree** - Self-balancing BST with O(log n) conflict detection
- **Max Heap** - Priority queue for urgency-based scheduling
- **Efficient pruning** - Branch-and-bound optimization

### 📊 Comprehensive Metrics
- Operating room utilization rates
- Average patient urgency scores
- Conflict detection and resolution
- Algorithm runtime comparison
- Scalability analysis (10, 20, 50+ surgeries)

### 💻 Dual Interface
- **CLI** - Batch processing with detailed reports
- **GUI** - Interactive tkinter interface with real-time updates

## Project Structure

```
Hospital Operating Room Scheduling Optimizer/
├── models.py              # Entity classes (Person, Surgeon, Patient, Surgery, etc.)
├── interval_tree.py       # Interval Tree data structure implementation
├── scheduler.py           # Scheduling algorithms (Greedy, Priority, Optimized)
├── hospital_manager.py    # Hospital system coordinator
├── cli.py                 # Command-line interface
├── gui.py                 # Graphical user interface
├── main.py                # Launcher (CLI/GUI selector)
└── README.md              # This file
```

## Quick Start

### Prerequisites
- Python 3.6 or higher
- No external dependencies (uses only standard library)

### Installation

```bash
# Clone or download the project
cd "Hospital Operating Room Scheduling Optimizer"

# Run with GUI (recommended for first-time users)
python main.py --gui

# Or run with CLI for full analysis
python main.py --cli
```

### Standard Library Modules Used
- `tkinter` - GUI framework
- `heapq` - Priority queue implementation
- `threading` - Multi-threaded GUI execution
- `time` - Performance measurement
- `abc` - Abstract base classes

## Usage

### Command-Line Interface (CLI)

Run the complete analysis with all schedulers and scalability tests:

```bash
python main.py --cli
```

Output includes:
- Individual scheduler results
- Performance comparison
- Scalability testing (10, 20, 50 surgeries)

### Graphical User Interface (GUI)

Launch the interactive GUI:

```bash
python main.py --gui
```

**GUI Features:**
- Initialize hospital with sample data
- Run individual schedulers
- Compare all schedulers side-by-side
- View metrics, schedules, and comparisons in tabbed interface
- Multi-threaded execution (non-blocking UI)

### Help

```bash
python main.py
```

## Technical Architecture

### 1. Model Layer (models.py)

**Person (Abstract Base Class)**
- `id`, `name`, `contact_info`

**Surgeon (extends Person)**
- `specialization`
- `assigned_surgeries` set (O(1) lookup)

**Patient (extends Person)**
- `urgency_score` (1-10)

**Surgery**
- Links patient, surgeon, operating room, and time slot
- Tracks scheduling status

**TimeSlot**
- Validates time boundaries (8 AM - 6 PM)
- Checks for overlaps

**OperatingRoom**
- Manages scheduled surgeries
- Calculates utilization rate

### 2. Data Structure Layer (interval_tree.py)

**Interval Tree**
- Self-balancing binary search tree
- Each node stores: interval, max_high value, height
- **Time Complexity:**
  - Insert: O(log n)
  - Delete: O(log n)
  - Search (overlap): O(log n)
- **Space Complexity:** O(n)

**Key Algorithm:**
```python
search_overlap(interval):
  if node.interval overlaps query:
    add to results
  if left exists and left.max_high >= query.start:
    search_overlap(left)
  if right exists and right.interval.start <= query.end:
    search_overlap(right)
```

### 3. Algorithm Layer (scheduler.py)

**Scheduler (Abstract Base Class)**
- Defines common interface: `run_schedule(surgeries)`
- Tracks runtime performance

**GreedyScheduler**
- **Strategy:** Earliest Finish Time (EFT)
- **Goal:** Maximize number of scheduled surgeries
- **Algorithm:** Sort by end time, schedule greedily
- **Time Complexity:** O(n log n) for sorting + O(n log n) for interval tree
- **Best for:** High throughput scenarios

**PriorityScheduler**
- **Strategy:** Max-heap by patient urgency
- **Goal:** Prioritize critical patients
- **Algorithm:** Pop highest urgency, schedule if no conflicts
- **Time Complexity:** O(n log n) for heap + O(n log n) for interval tree
- **Best for:** Patient safety and urgency-driven scheduling

**OptimizedScheduler**
- **Strategy:** Branch-and-bound with pruning
- **Goal:** Minimize total idle time across all rooms
- **Algorithm:** Recursive exploration with early termination
- **Optimizations:**
  - Prunes branches that exceed current best idle time
  - Checks both room and surgeon conflicts
  - Sorts by duration (longest first) for better pruning
- **Time Complexity:** O(2^n) worst case, significantly pruned in practice
- **Best for:** Resource efficiency and cost optimization

### 4. Core System Layer (hospital_manager.py)

**Hospital**
- Manages operating rooms and surgeries
- Maintains interval tree for conflict detection
- Generates utilization reports
- Tracks performance metrics

### 5. Interface Layer

**CLI (cli.py)**
- Batch processing of all schedulers
- Scalability testing
- Console output

**GUI (gui.py)**
- Interactive tkinter interface
- Real-time results display
- Multi-threaded execution

## Performance Analysis

### Conflict Detection Efficiency

| Approach | Time Complexity | Space Complexity | Operations for 1000 surgeries |
|----------|-----------------|------------------|-------------------------------|
| Linear Scan | O(n) | O(1) | ~1000 comparisons |
| Interval Tree | O(log n) | O(n) | ~10 comparisons |

**Speedup:** ~100x faster for large datasets

### Scheduler Comparison

| Scheduler | Strategy | Time Complexity | Best For | Trade-offs |
|-----------|----------|-----------------|----------|------------|
| Greedy | Earliest Finish Time | O(n log n) | High throughput | May ignore urgency |
| Priority | Patient Urgency | O(n log n) | Patient safety | May reduce utilization |
| Optimized | Branch-and-Bound | O(2^n) pruned | Resource efficiency | Slower for large datasets |

## Example Output

```
Hospital Operating Room Scheduling Optimizer
============================================================

============================================================
Running Greedy Scheduler (Earliest Finish Time)
============================================================
Surgeries scheduled: 8/8
Algorithm runtime: 0.000035 seconds
Conflicts detected: 0

Scheduled Surgeries:
  SUR000: John Doe - Dr. Smith - OR001 - TimeSlot(8:00-10:00)
  ...

Performance Metrics:
  Total Surgeries Scheduled: 8
  Operating Rooms: 3
  Average Utilization: 53.33%
  Average Urgency Score: 7.38
  Conflicts Detected: 0
```

## Scalability Testing

The CLI automatically tests all schedulers with increasing dataset sizes:
- **10 surgeries** - Baseline performance
- **20 surgeries** - Medium-scale testing
- **50 surgeries** - Large-scale stress testing

Results demonstrate:
- Greedy and Priority schedulers maintain O(n log n) performance
- Optimized scheduler shows exponential growth but remains practical with pruning
- Interval tree provides consistent O(log n) conflict detection

## Design Principles

1. **Encapsulation** - Clear separation of concerns across modules
2. **Polymorphism** - Scheduler base class with multiple implementations
3. **Efficiency** - O(log n) conflict detection vs O(n) linear scan
4. **Modularity** - Independent, reusable components
5. **Validation** - Input validation at entity level (time slots, urgency scores)
6. **Thread Safety** - GUI uses locks and queues for concurrent execution
7. **Immutability** - Safe copying of best solutions in branch-and-bound

## Algorithm Improvements Made

### OptimizedScheduler Enhancements
1. **Pruning** - Early termination when current idle time exceeds best found
2. **Surgeon conflict detection** - Prevents double-booking surgeons
3. **Accurate idle time calculation** - Counts all hospital rooms, not just used ones
4. **Safe best-schedule handling** - Uses list copying instead of mutation

## Future Enhancements

- **Data Import** - CSV/JSON file support for real hospital data
- **Advanced Constraints** - Equipment requirements, surgeon specialization matching
- **Real-time Updates** - Dynamic rescheduling for emergencies
- **Visualization** - Gantt charts and timeline views
- **Machine Learning** - Predictive surgery duration modeling
- **Multi-day Scheduling** - Extended planning horizons
- **Export Reports** - PDF/Excel report generation

## Acknowledgments

- Course instructors for project guidance
- Python standard library documentation
- Algorithm design principles from course materials

## License

Educational use only. This project is submitted as coursework for COMP 2090SEF.

---

**Note:** This system demonstrates algorithmic problem-solving and data structure implementation for educational purposes. For production hospital systems, additional safety validations, regulatory compliance, and real-time constraints would be required.
