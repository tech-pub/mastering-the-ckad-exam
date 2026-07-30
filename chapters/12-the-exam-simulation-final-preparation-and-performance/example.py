import time
import random

# Core concept: Simulating a timed exam with various 'tasks' and a limited time budget.
# This helps practice efficient problem-solving under pressure, much like the CKAD exam.


# --- Exam Simulation Parameters ---
EXAM_DURATION_MINUTES = 10  # Reduced for demonstration purposes (CKAD is usually 120 mins)
TOTAL_TASKS = 5
AVERAGE_TASK_TIME_SECONDS = (EXAM_DURATION_MINUTES * 60) / TOTAL_TASKS


# --- Task Definitions (Simplified for demonstration) ---
def task_one():
    """Simulates a simple K8s task like creating a Pod."""
    time.sleep(random.uniform(2, 5))  # Simulate varying completion times
    return "Pod created successfully."

def task_two():
    """Simulates a task requiring resource inspection, e.g., 'kubectl get pod -o yaml'."""
    time.sleep(random.uniform(4, 8))
    return "Resource inspected and data extracted."

def task_three():
    """Simulates a task like deploying a Deployment from a manifest."""
    time.sleep(random.uniform(3, 7))
    return "Deployment applied and scaled."

def task_four():
    """Simulates debugging a failing application in a Pod."""
    time.sleep(random.uniform(5, 10))
    return "Application debugged and issue identified."

def task_five():
    """Simulates a network-related task, e.g., exposing a service."""
    time.sleep(random.uniform(3, 6))
    return "Service exposed and accessible."

# Store tasks in a list for iteration
EXAM_TASKS = [task_one, task_two, task_three, task_four, task_five]


# --- Exam Simulator Function ---
def run_mock_exam():
    """
    Simulates a CKAD-like exam experience with timed tasks.
    Focuses on time management and task completion under pressure.
    """
    print(f"--- Starting Mock CKAD Exam ---")
    print(f"Duration: {EXAM_DURATION_MINUTES} minutes, Total Tasks: {TOTAL_TASKS}")
    print(f"Estimated time per task: {AVERAGE_TASK_TIME_SECONDS:.0f} seconds\n")

    start_time = time.time()
    successful_tasks = 0

    for i, task in enumerate(EXAM_TASKS):
        current_task_start = time.time()
        time_elapsed = current_task_start - start_time
        remaining_time = (EXAM_DURATION_MINUTES * 60) - time_elapsed

        if remaining_time <= 0:
            print(f"Time's up! Cannot start Task {i+1}. Remaining tasks incomplete.")
            break

        print(f"-> Starting Task {i+1}/{TOTAL_TASKS} (Time Remaining: {remaining_time:.0f}s)")
        print(f"   Executing '{task.__name__}'...")

        try:
            # Simulate the work needed for a task
            task_result = task()
            task_duration = time.time() - current_task_start
            print(f"   Task {i+1} completed in {task_duration:.2f}s. Result: {task_result}")
            successful_tasks += 1
        except Exception as e:
            print(f"   Task {i+1} failed: {e}")
        print("-" * 30)

    end_time = time.time()
    total_exam_time = end_time - start_time

    print(f"\n--- Mock Exam Finished ---")
    print(f"Total time taken: {total_exam_time:.2f} seconds")
    print(f"Tasks completed successfully: {successful_tasks}/{TOTAL_TASKS}")

    if total_exam_time > (EXAM_DURATION_MINUTES * 60):
        print("Result: EXAM TIMEOUT. Time management is crucial!")
    elif successful_tasks == TOTAL_TASKS:
        print("Result: All tasks completed within time. Excellent performance!")
    else:
        print("Result: Some tasks incomplete. Review time management and task efficiency.")

# Run the simulation
if __name__ == "__main__":
    run_mock_exam()
