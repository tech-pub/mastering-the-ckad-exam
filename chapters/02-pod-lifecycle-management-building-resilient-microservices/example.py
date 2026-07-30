import time
import threading

class Container:
    """Simulates a single application container."""
    def __init__(self, name, crash_probability=0.2):
        self.name = name
        self.crash_probability = crash_probability
        self.running = False
        self.health_checks = 0

    def start(self):
        """Starts the container."""
        print(f"Container '{self.name}': Starting...")
        self.running = True
        self.health_checks = 0
        print(f"Container '{self.name}': Started.")

    def stop(self):
        """Stops the container."""
        print(f"Container '{self.name}': Stopping...")
        self.running = False
        print(f"Container '{self.name}': Stopped.")

    def is_healthy(self):
        """Simulates a health check. May randomly fail."""
        self.health_checks += 1
        if self.running and self.health_checks % 5 != 0: # Simulate occasional crashes
            # print(f"Container '{self.name}': Healthy (check {self.health_checks}).")
            return True
        else:
            print(f"Container '{self.name}': Unhealthy or crashed! (check {self.health_checks}).")
            return False

class Pod:
    """Manages the lifecycle of a single container for resilience."""
    def __init__(self, container_name):
        self.container = Container(container_name)
        self.monitoring_thread = None
        self.running_pod = False

    def start(self):
        """Starts the pod, including its container and health monitoring."""
        print(f"\nPod '{self.container.name}': Starting...")
        self.running_pod = True
        self.container.start()
        self.monitoring_thread = threading.Thread(target=self._monitor_container)
        self.monitoring_thread.daemon = True  # Allows program to exit if main thread stops
        self.monitoring_thread.start()
        print(f"Pod '{self.container.name}': Started with monitoring.")

    def stop(self):
        """Stops the pod and its container."""
        print(f"\nPod '{self.container.name}': Stopping...")
        self.running_pod = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1) # Wait for monitoring to stop
        self.container.stop()
        print(f"Pod '{self.container.name}': Stopped.")

    def _monitor_container(self):
        """Continuously checks container health and restarts if necessary."""
        while self.running_pod:
            if not self.container.is_healthy():
                print(f"Pod '{self.container.name}': Detecting unhealthy container - restarting!")
                self.container.stop()
                self.container.start()
            time.sleep(0.5) # Simulate health check interval

# --- Simulation ---
if __name__ == "__main__":
    app_pod = Pod("my-microservice")

    app_pod.start()
    print("\n--- Pod is running and self-healing. Simulating external workload... ---")
    time.sleep(8)  # Let the pod run and potentially self-heal multiple times

    app_pod.stop()
    print("\nSimulation Finished.")
