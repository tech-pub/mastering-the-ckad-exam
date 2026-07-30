# This example simulates interacting with a Kubernetes-like API
# to demonstrate the declarative model and resource navigation.
# No actual Kubernetes cluster is needed.

class KubernetesResource:
    """Represents a generic Kubernetes resource."""
    def __init__(self, api_version, kind, metadata, spec):
        self.api_version = api_version
        self.kind = kind
        self.metadata = metadata
        self.spec = spec
        self.status = {} # Status is typically managed by controllers

    def to_dict(self):
        """Converts the resource to a dictionary (YAML/JSON representation)."""
        return {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": self.metadata,
            "spec": self.spec,
            "status": self.status
        }

class MockKubeAPI:
    """A very basic mock Kubernetes API server."""
    def __init__(self):
        self._resources = {} # Stores resources by kind and name

    def apply(self, resource_yaml):
        """Simulates 'kubectl apply'. Creates or updates a resource."""
        resource = KubernetesResource(
            resource_yaml['apiVersion'],
            resource_yaml['kind'],
            resource_yaml['metadata'],
            resource_yaml['spec']
        )
        kind = resource.kind.lower()
        name = resource.metadata['name']

        if kind not in self._resources:
            self._resources[kind] = {}

        if name in self._resources[kind]:
            print(f"Updating existing {kind}/{name}")
        else:
            print(f"Creating new {kind}/{name}")

        self._resources[kind][name] = resource
        return resource

    def get(self, kind, name=None):
        """Simulates 'kubectl get'. Retrieves resources."""
        kind_lower = kind.lower()
        if kind_lower not in self._resources:
            print(f"No resources of kind '{kind}' found.")
            return [] if name is None else None

        if name:
            resource = self._resources[kind_lower].get(name)
            if resource:
                return resource.to_dict()
            print(f"Resource {kind}/{name} not found.")
            return None
        else:
            return [res.to_dict() for res in self._resources[kind_lower].values()]

# --- Example Usage ---

if __name__ == "__main__":
    mock_api = MockKubeAPI()

    # Define a Deployment (declarative state)
    deployment_yaml = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "my-nginx-deployment", "labels": {"app": "nginx"}},
        "spec": {
            "replicas": 3,
            "selector": {"matchLabels": {"app": "nginx"}},
            "template": {
                "metadata": {"labels": {"app": "nginx"}},
                "spec": {"containers": [{"name": "nginx", "image": "nginx:latest"}]}
            }
        }
    }

    # Apply the Deployment (declarative action)
    print("\n--- Applying Deployment ---")
    mock_api.apply(deployment_yaml)

    # Define a Service
    service_yaml = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": "my-nginx-service", "labels": {"app": "nginx"}},
        "spec": {
            "selector": {"app": "nginx"},
            "ports": [{"protocol": "TCP", "port": 80, "targetPort": 80}]
        }
    }

    # Apply the Service
    print("\n--- Applying Service ---")
    mock_api.apply(service_yaml)

    # --- Navigating Resources (kubectl get like behavior) ---
    print("\n--- Getting all deployments ---")
    print(mock_api.get("Deployment"))

    print("\n--- Getting a specific service ---")
    print(mock_api.get("Service", "my-nginx-service"))

    print("\n--- Attempting to get a non-existent resource ---")
    print(mock_api.get("Pod", "non-existent-pod"))

    # Update the Deployment (change replicas from 3 to 1) and re-apply
    print("\n--- Updating Deployment (changing replicas) ---")
    deployment_yaml['spec']['replicas'] = 1
    mock_api.apply(deployment_yaml)
    print("\n--- Getting updated deployment ---")
    print(mock_api.get("Deployment", "my-nginx-deployment"))
