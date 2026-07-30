import os
import shutil

class Pod:
    """
    Represents a Kubernetes Pod that can process data.
    Simulates the ephemeral nature of Pods.
    """
    def __init__(self, name, volume_mount_path=None):
        self.name = name
        self.volume_mount_path = volume_mount_path
        print(f"Pod '{self.name}' created.")

    def process_data(self, data):
        """Processes data and tries to save it."""
        if self.volume_mount_path:
            # If a volume is mounted, save data there
            filepath = os.path.join(self.volume_mount_path, "processed_data.txt")
            with open(filepath, "w") as f:
                f.write(data)
            print(f"Pod '{self.name}': Data saved to mounted volume at {filepath}")
        else:
            # Without a volume, data is stored ephemerally within the pod's "filesystem"
            self.internal_data = data
            print(f"Pod '{self.name}': Data processed and stored internally (ephemeral).")

    def __del__(self):
        print(f"Pod '{self.name}' terminated. All internal data lost.")


class Volume:
    """
    Simulates a persistent storage Volume that can be mounted by Pods.
    """
    def __init__(self, name, path):
        self.name = name
        self.path = path
        os.makedirs(self.path, exist_ok=True)
        print(f"Volume '{self.name}' created at '{self.path}'.")

    def cleanup(self):
        """Cleans up the volume's directory."""
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
            print(f"Volume '{self.name}' at '{self.path}' cleaned up.")


# --- Simulation of Kubernetes behavior ---

if __name__ == "__main__":
    # Scenario 1: Pod without a persistent volume (data loss)
    print("\n--- Scenario 1: Pod without Volume (Ephemeral) ---")
    pod1 = Pod("ephemeral-pod")
    pod1.process_data("Ephemeral data for Pod 1")
    # Pod terminates, data is lost
    del pod1
    # If we tried to access pod1.internal_data here, it would fail

    # Scenario 2: Pod with a persistent volume (data persists)
    print("\n--- Scenario 2: Pod with Volume (Persistent) ---")
    volume_path = "./persistent-storage-data"
    p_volume = Volume("my-persistent-volume", volume_path)

    # First Pod mounts the volume, writes data
    pod2_a = Pod("pod-with-vol-a", volume_mount_path=p_volume.path)
    pod2_a.process_data("Persistent data from Pod A")
    del pod2_a # Pod terminates

    # A new Pod starts, mounts the *same* volume, and can access the data
    print("\n--- Pod A terminated, Pod B starts and mounts the same volume ---")
    pod2_b = Pod("pod-with-vol-b", volume_mount_path=p_volume.path)
    persisted_filepath = os.path.join(p_volume.path, "processed_data.txt")
    if os.path.exists(persisted_filepath):
        with open(persisted_filepath, "r") as f:
            retrieved_data = f.read()
        print(f"Pod '{pod2_b.name}': Retrieved data from volume: '{retrieved_data}'")
    else:
        print(f"Pod '{pod2_b.name}': No data found in volume.")
    del pod2_b # Pod terminates

    # Clean up the persistent volume entirely
    p_volume.cleanup()
