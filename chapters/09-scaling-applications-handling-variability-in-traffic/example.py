import collections
import random
import time

# --- Simulate Core Idea: Horizontal Pod Autoscaler (HPA) logic ---

# Represents a single 'pod' processing requests.
class Pod:
    def __init__(self, pod_id):
        self.pod_id = pod_id
        self.processing_request = False
        self.cpu_usage = 0.0 # Simulate CPU usage for demonstration

    def process_request(self):
        # Simulate work being done, increasing CPU usage temporarily
        self.processing_request = True
        self.cpu_usage = random.uniform(0.5, 0.9)  # High usage during processing
        time.sleep(random.uniform(0.01, 0.05)) # Simulate processing time
        self.processing_request = False
        self.cpu_usage = random.uniform(0.1, 0.3)  # Low usage when idle
        # print(f"Pod {self.pod_id} processed a request.")

# Manages the fleet of pods based on metrics.
class HPA:
    def __init__(self, min_pods=2, max_pods=10, target_cpu_percent=50):
        self.min_pods = min_pods
        self.max_pods = max_pods
        self.target_cpu_percent = target_cpu_percent
        self.pods = collections.deque([Pod(i) for i in range(min_pods)])
        self.next_pod_id = min_pods # For assigning IDs to new pods

    def get_average_cpu_usage(self):
        if not self.pods:
            return 0.0
        total_cpu = sum(p.cpu_usage for p in self.pods if p.cpu_usage > 0)
        return (total_cpu / len(self.pods)) * 100 # Convert to percentage

    def scale_logic(self):
        avg_cpu = self.get_average_cpu_usage()
        # print(f"Current average CPU usage: {avg_cpu:.2f}% with {len(self.pods)} pods.")

        # Scale out: If average CPU is above target and we haven't reached max pods
        if avg_cpu > self.target_cpu_percent and len(self.pods) < self.max_pods:
            new_pod = Pod(self.next_pod_id)
            self.pods.append(new_pod)
            self.next_pod_id += 1
            print(f"HPA: Scaling out! Added Pod {new_pod.pod_id}. Total pods: {len(self.pods)}")
        # Scale in: If average CPU is significantly below target and we have more than min pods
        elif avg_cpu < (self.target_cpu_percent * 0.7) and len(self.pods) > self.min_pods:
            removed_pod = self.pods.popleft() # Remove the oldest pod
            print(f"HPA: Scaling in! Removed Pod {removed_pod.pod_id}. Total pods: {len(self.pods)}")

    def dispatch_request(self):
        if not self.pods:
            print("No pods available to process requests!")
            return False

        # Find an available pod or use the first one if all are busy
        available_pod = None
        for pod in self.pods:
            if not pod.processing_request:
                available_pod = pod
                break
        if available_pod is None:
            available_pod = self.pods[0] # All pods busy, overload first one

        available_pod.process_request()
        return True


# --- Simulation Run ---
if __name__ == "__main__":
    hpa_controller = HPA(min_pods=2, max_pods=5, target_cpu_percent=60)
    print(f"HPA simulation started with initial {len(hpa_controller.pods)} pods.")

    simulation_steps = 20
    print("\n--- Initial state ---")
    hpa_controller.scale_logic() # Check initial state

    for step in range(simulation_steps):
        print(f"\n--- Step {step + 1} ---")
        # Simulate incoming traffic - more requests can lead to higher CPU
        num_requests = random.randint(1, 5) if step < 10 else random.randint(5, 12) # Simulate a traffic spike
        print(f"Incoming traffic: {num_requests} requests.")

        for _ in range(num_requests):
            hpa_controller.dispatch_request()

        # HPA evaluates and scales periodically
        hpa_controller.scale_logic()
        time.sleep(0.5) # Simulate time passing between HPA checks
