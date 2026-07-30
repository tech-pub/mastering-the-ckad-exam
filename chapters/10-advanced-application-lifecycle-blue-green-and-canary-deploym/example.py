import time
import requests # For simulating external requests
import threading # For concurrent execution

class SimpleService:
    """A simple service that returns a version string."""
    def __init__(self, version):
        self.version = version

    def get_version(self):
        return f"Service Version: {self.version}"

class DeploymentManager:
    """Simulates a deployment manager for zero-downtime updates."""
    def __init__(self, initial_version):
        self.active_service = SimpleService(initial_version)
        print(f"Deployment Manager initialized with: {self.active_service.get_version()}")

    def _simulate_traffic(self, duration_s):
        """Simulates client requests to the active service."""
        start_time = time.time()
        while time.time() - start_time < duration_s:
            try:
                # Simulate a request to the active service
                current_version = self.active_service.get_version()
                print(f"Client request received: {current_version}")
            except Exception as e:
                print(f"Client request failed: {e}")
            time.sleep(0.5) # Simulate request interval

    def blue_green_deploy(self, new_version):
        """Performs a blue-green deployment."""
        print(f"\n--- Starting Blue-Green Deployment to {new_version} ---")

        # 1. Create the new 'green' environment
        new_service = SimpleService(new_version)
        print(f"Spinning up new 'green' service: {new_service.get_version()}")
        time.sleep(2) # Simulate startup time

        # 2. Simulate traffic to blue while green is warming up
        print("Pre-switchover traffic to 'blue' (old version)...")
        traffic_thread = threading.Thread(target=self._simulate_traffic, args=(5,))
        traffic_thread.start()
        traffic_thread.join() # Wait for some initial traffic to pass

        # 3. Switch traffic to the new 'green' environment
        print(f"Switching traffic from '{self.active_service.version}' to '{new_service.version}' (instantaneously)...")
        self.active_service = new_service
        print(f"Traffic now routed to: {self.active_service.get_version()}")

        # 4. Monitor 'green' and potentially decommission 'blue'
        print("Monitoring new 'green' service and decommissioning 'blue' (old version)...")
        traffic_thread = threading.Thread(target=self._simulate_traffic, args=(5,))
        traffic_thread.start()
        traffic_thread.join()

        print(f"--- Blue-Green Deployment to {new_version} Complete ---")

if __name__ == "__main__":
    manager = DeploymentManager("v1.0")

    # Simulate some initial traffic
    print("\nInitial traffic to v1.0:")
    manager._simulate_traffic(5)

    # Perform a blue-green deploy
    manager.blue_green_deploy("v2.0")

    # Simulate more traffic after deployment
    print("\nTraffic after v2.0 deployment:")
    manager._simulate_traffic(5)

    # Perform another blue-green deploy
    manager.blue_green_deploy("v2.1-hotfix")
