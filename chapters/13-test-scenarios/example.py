import traceback

def run_test_scenario(scenario_func, scenario_name):
    """
    Executes a given test scenario function and reports its success or failure.
    """
    print(f"--- Running Scenario: {scenario_name} ---")
    try:
        scenario_func()
        print(f"Scenario '{scenario_name}' PASSED.")
    except AssertionError as e:
        print(f"Scenario '{scenario_name}' FAILED: {e}")
        traceback.print_exc() # Print full traceback for detailed debugging
    except Exception as e:
        print(f"Scenario '{scenario_name}' ENCOUNTERED UNEXPECTED ERROR: {e}")
        traceback.print_exc() # Print full traceback for detailed debugging
    print(f"--- End Scenario: {scenario_name} ---\n")

# Mock Kubernetes API interactions for testing purposes
class MockKubeClient:
    def __init__(self):
        self.pods = []
        self.deployments = []
        self.services = []

    def create_pod(self, pod_name, labels):
        self.pods.append({'name': pod_name, 'labels': labels, 'status': 'Running'})
        return {'status': 'success'}

    def get_pods_with_label(self, label_key, label_value):
        return [p for p in self.pods if p['labels'].get(label_key) == label_value]

    def delete_pod(self, pod_name):
        initial_len = len(self.pods)
        self.pods = [p for p in self.pods if p['name'] != pod_name]
        return {'status': 'success'} if initial_len > len(self.pods) else {'status': 'not_found'}

    def create_deployment(self, name, replicas, image):
        self.deployments.append({'name': name, 'replicas': replicas, 'image': image})
        return {'status': 'success'}

    def scale_deployment(self, name, new_replicas):
        for dep in self.deployments:
            if dep['name'] == name:
                dep['replicas'] = new_replicas
                return {'status': 'success'}
        return {'status': 'not_found'}

# --- CKAD Mock Test Scenarios ---

def scenario_create_and_verify_pod():
    """
    Scenario 1: Create a pod and verify its creation.
    Equivalent to: kubectl run my-pod --image=nginx
    """
    kube = MockKubeClient()
    pod_name = "my-nginx-pod"
    kube.create_pod(pod_name, {'app': 'nginx'})

    # Assertions for verification
    found_pods = kube.get_pods_with_label('app', 'nginx')
    assert len(found_pods) == 1, f"Expected 1 pod, got {len(found_pods)}"
    assert found_pods[0]['name'] == pod_name, f"Pod name mismatch: {found_pods[0]['name']}"
    print(f"Pod '{pod_name}' created and verified successfully.")

def scenario_scale_deployment():
    """
    Scenario 2: Create a deployment and then scale it.
    Equivalent to: kubectl create deployment my-app --image=busybox
    then: kubectl scale deployment my-app --replicas=3
    """
    kube = MockKubeClient()
    deployment_name = "my-scalable-app"
    initial_replicas = 1
    target_replicas = 3

    kube.create_deployment(deployment_name, initial_replicas, "busybox")
    # Verify initial state
    assert kube.deployments[0]['replicas'] == initial_replicas, "Initial replicas mismatch"

    kube.scale_deployment(deployment_name, target_replicas)
    # Verify scaled state
    found_deployment = next((d for d in kube.deployments if d['name'] == deployment_name), None)
    assert found_deployment is not None, "Deployment not found after scaling attempt"
    assert found_deployment['replicas'] == target_replicas, \
           f"Expected {target_replicas} replicas, got {found_deployment['replicas']}"
    print(f"Deployment '{deployment_name}' scaled to {target_replicas} replicas.")

def scenario_delete_pod_and_verify():
    """
    Scenario 3: Create a pod, then delete it and verify its absence.
    Equivalent to: kubectl run my-temp-pod --image=ubuntu
    then: kubectl delete pod my-temp-pod
    """
    kube = MockKubeClient()
    pod_name = "my-temp-pod"
    kube.create_pod(pod_name, {'temp': 'true'})

    # Verify creation
    assert len(kube.get_pods_with_label('temp', 'true')) == 1, "Pod not created for deletion test"

    kube.delete_pod(pod_name)

    # Verify deletion
    assert len(kube.get_pods_with_label('temp', 'true')) == 0, "Pod still exists after deletion attempt"
    print(f"Pod '{pod_name}' deleted and verified successfully.")


# --- Main execution loop for scenarios ---
if __name__ == "__main__":
    scenarios = [
        (scenario_create_and_verify_pod, "Create and Verify Pod"),
        (scenario_scale_deployment, "Scale Deployment"),
        (scenario_delete_pod_and_verify, "Delete Pod and Verify Absence")
    ]

    print("Starting CKAD Mock Test Scenarios...\n")
    for scenario_func, scenario_name in scenarios:
        run_test_scenario(scenario_func, scenario_name)
    print("All CKAD Mock Test Scenarios Completed.")
