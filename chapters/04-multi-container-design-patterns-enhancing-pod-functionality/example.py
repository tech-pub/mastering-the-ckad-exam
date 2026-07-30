import time
import os

class MainApplication:
    """Represents the primary application container."""
    def run(self):
        print(f"[{time.ctime()}] MainApplication: Starting to process data.")
        time.sleep(2)  # Simulate work
        print(f"[{time.ctime()}] MainApplication: Data processing complete.")
        return "ProcessedDataChunk"

class SidecarLogger:
    """Sidecar pattern: Handles logging for the main application."""
    def log_activity(self, activity_data):
        log_entry = f"[{time.ctime()}] SidecarLogger: Log event - {activity_data}"
        print(log_entry)
        # In a real scenario, this would write to a shared volume or remote logging service.
        with open("application.log", "a") as f:
            f.write(log_entry + "\n")

class AmbassadorProxy:
    """Ambassador pattern: Manages external communication or configuration."""
    def __init__(self, target_service_url="http://real-api.example.com"):
        self.target_service_url = target_service_url

    def get_data(self, endpoint):
        print(f"[{time.ctime()}] AmbassadorProxy: Intercepting request for {endpoint}")
        # In a real scenario, this would perform actual network requests
        # and potentially apply caching, retries, or authentication.
        simulated_response = f"Data from '{self.target_service_url}/api/{endpoint}'"
        print(f"[{time.ctime()}] AmbassadorProxy: Forwarded request, got '{simulated_response}'")
        return simulated_response

class Pod:
    """Represents a Kubernetes Pod with multiple containers."""
    def __init__(self):
        self.main_app = MainApplication()
        self.logger = SidecarLogger()
        self.proxy = AmbassadorProxy()

    def start(self):
        print("\n--- Pod Starting ---")
        # Main application performs its core task
        result = self.main_app.run()
        self.logger.log_activity(f"Main application finished with result: '{result}'")

        # Main application (or another service within the Pod) needs external data
        external_data = self.proxy.get_data("metrics")
        self.logger.log_activity(f"Retrieved external data via Ambassador: '{external_data}'")
        print("--- Pod Finished ---\n")

if __name__ == "__main__":
    # Clean up previous log file for a fresh run
    if os.path.exists("application.log"):
        os.remove("application.log")

    my_pod = Pod()
    my_pod.start()

    print("\n--- Content of application.log ---")
    with open("application.log", "r") as f:
        print(f.read())
