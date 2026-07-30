import base64
import json
import os

# --- Simulate Kubernetes API Objects (simplified for demonstration) ---

class Resource:
    def __init__(self, kind, name, namespace="default", apiVersion="v1"):
        self.kind = kind
        self.name = name
        self.namespace = namespace
        self.apiVersion = apiVersion
        self.data = {} # For secrets, configmaps, etc.

    def __repr__(self):
        return f"{self.kind}/{self.name} (namespace: {self.namespace})"

class APIServer:
    def __init__(self):
        self.objects = {
            "ServiceAccount": {},
            "Role": {},
            "RoleBinding": {},
            "Pod": {},
            "Secret": {}
        }

    def create(self, obj):
        if obj.kind not in self.objects:
            raise ValueError(f"Unsupported kind: {obj.kind}")
        if obj.namespace not in self.objects[obj.kind]:
            self.objects[obj.kind][obj.namespace] = {}
        self.objects[obj.kind][obj.namespace][obj.name] = obj
        print(f"Created {obj.kind}/{obj.name} in namespace {obj.namespace}")

    def get(self, kind, name, namespace="default"):
        return self.objects.get(kind, {}).get(namespace, {}).get(name)

    def authorize(self, subject, verb, resource_kind, resource_name=None, namespace="default"):
        """
        Simulates RBAC authorization.
        Checks if the subject (ServiceAccount) has permission for the action.
        """
        # 1. Find RoleBindings for the subject in the namespace
        applicable_bindings = []
        for binding_name, binding in self.objects["RoleBinding"].get(namespace, {}).items():
            for s in binding.data.get("subjects", []):
                if s.get("kind") == "ServiceAccount" and s.get("name") == subject.name:
                    applicable_bindings.append(binding)
                    break # Found a binding for this SA

        if not applicable_bindings:
            print(f"Authorization Denied: No RoleBinding found for ServiceAccount '{subject.name}' in namespace '{namespace}'.")
            return False

        # 2. For each applicable binding, find its Role
        for binding in applicable_bindings:
            role_ref = binding.data.get("roleRef")
            if not role_ref:
                continue

            role_kind = role_ref.get("kind")
            role_name = role_ref.get("name")
            role_namespace = binding.namespace # Roles are typically namespaced with RoleBindings

            role = self.get(role_kind, role_name, role_namespace)
            if not role:
                print(f"Warning: Role '{role_name}' referenced by RoleBinding '{binding.name}' not found.")
                continue

            # 3. Check Role's rules for the requested verb and resource
            for rule in role.data.get("rules", []):
                api_groups = rule.get("apiGroups", [""]) # default to core API group
                resources = rule.get("resources", [])
                verbs = rule.get("verbs", [])

                if (verb in verbs and
                    (resource_kind in resources or "*" in resources)):
                    print(f"Authorization Granted: ServiceAccount '{subject.name}' can '{verb}' '{resource_kind}' via Role '{role.name}'.")
                    return True

        print(f"Authorization Denied: ServiceAccount '{subject.name}' does not have '{verb}' permission for '{resource_kind}' in namespace '{namespace}'.")
        return False

# --- Main Simulation ---
if __name__ == "__main__":
    k8s = APIServer()

    # 1. Create a ServiceAccount for an application
    app_sa = Resource("ServiceAccount", "data-reader-sa", namespace="default")
    k8s.create(app_sa)

    # 2. Define a Role with specific permissions (read-only for pods)
    pod_reader_role = Resource("Role", "pod-reader", namespace="default")
    pod_reader_role.data = {
        "rules": [
            {
                "apiGroups": [""],  # "" indicates the core API group
                "resources": ["pods", "pods/log"],
                "verbs": ["get", "watch", "list"]
            },
            {
                "apiGroups": ["apps"],
                "resources": ["deployments"],
                "verbs": ["get", "watch", "list"]
            }
        ]
    }
    k8s.create(pod_reader_role)

    # 3. Bind the ServiceAccount to the Role
    reader_role_binding = Resource("RoleBinding", "read-pods-binding", namespace="default")
    reader_role_binding.data = {
        "subjects": [
            {"kind": "ServiceAccount", "name": "data-reader-sa", "namespace": "default"}
        ],
        "roleRef": {
            "kind": "Role",
            "name": "pod-reader",
            "apiGroup": "rbac.authorization.k8s.io"
        }
    }
    k8s.create(reader_role_binding)

    # --- Test Authorization ---

    # Scenario 1: Reader tries to list pods (allowed)
    print("\n--- Testing authorization for data-reader-sa ---")
    k8s.authorize(app_sa, "list", "pods", namespace="default") # Should be Granted
    k8s.authorize(app_sa, "get", "deployments", namespace="default") # Should be Granted

    # Scenario 2: Reader tries to create secrets (not allowed)
    k8s.authorize(app_sa, "create", "secrets", namespace="default") # Should be Denied

    # Scenario 3: Reader tries to delete pods (not allowed)
    k8s.authorize(app_sa, "delete", "pods", namespace="default") # Should be Denied

    # Scenario 4: Create another ServiceAccount and try unauthorized action
    unprivileged_sa = Resource("ServiceAccount", "unprivileged-sa", namespace="default")
    k8s.create(unprivileged_sa)
    print("\n--- Testing authorization for unprivileged-sa (no role binding) ---")
    k8s.authorize(unprivileged_sa, "list", "pods", namespace="default") # Should be Denied

    # --- Demonstrate a more powerful role (e.g., for an admin) ---
    admin_sa = Resource("ServiceAccount", "admin-sa", namespace="default")
    k8s.create(admin_sa)

    admin_role = Resource("Role", "admin-all-resources", namespace="default")
    admin_role.data = {
        "rules": [
            {
                "apiGroups": ["*"],          # All API groups
                "resources": ["*"],          # All resources
                "verbs": ["*"]               # All verbs
            }
        ]
    }
    k8s.create(admin_role)

    admin_role_binding = Resource("RoleBinding", "admin-binding", namespace="default")
    admin_role_binding.data = {
        "subjects": [
            {"kind": "ServiceAccount", "name": "admin-sa", "namespace": "default"}
        ],
        "roleRef": {
            "kind": "Role",
            "name": "admin-all-resources",
            "apiGroup": "rbac.authorization.k8s.io"
        }
    }
    k8s.create(admin_role_binding)

    print("\n--- Testing authorization for admin-sa ---")
    k8s.authorize(admin_sa, "create", "pods", namespace="default")    # Should be Granted
    k8s.authorize(admin_sa, "delete", "secrets", namespace="default") # Should be Granted
