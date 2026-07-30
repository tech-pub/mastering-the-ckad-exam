import http.server
import socketserver
import threading
import time
import requests

# --- Microservice A (Service to be called) ---
class MicroserviceAHandler(http.server.BaseHTTPRequestHandler):
    """
    A simple HTTP handler for Microservice A, which responds to greetings.
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Hello from Microservice A!")

def run_microservice_a(port):
    """Starts Microservice A on a given port."""
    with socketserver.TCPServer(("", port), MicroserviceAHandler) as httpd:
        print(f"Microservice A serving on port {port}")
        httpd.serve_forever()

# --- Microservice B (Client calling Microservice A, simulating inter-service communication) ---
class MicroserviceB:
    """
    Simulates a client microservice that calls Microservice A.
    In a real Kubernetes cluster, this would use a Service name for discovery.
    """
    def __init__(self, service_a_host, service_a_port):
        self.service_a_url = f"http://{service_a_host}:{service_a_port}"

    def call_service_a(self):
        """Attempts to call Microservice A and returns its response."""
        try:
            print(f"Microservice B attempting to call: {self.service_a_url}")
            response = requests.get(self.service_a_url, timeout=2)
            response.raise_for_status()  # Raise an exception for bad status codes
            return f"Microservice B received: {response.text}"
        except requests.exceptions.ConnectionError as e:
            return f"Microservice B failed to connect to A: {e}"
        except requests.exceptions.RequestException as e:
            return f"Microservice B encountered an error: {e}"

# --- Simulating Kubernetes Service concept (abstracting Microservice A's direct port) ---
class KubernetesServiceSimulator:
    """
    This class simulates how Kubernetes Service discovery works.
    Clients (like Microservice B) would refer to 'service_a_name'
    and the K8s DNS would resolve it to the actual pod IP/port.
    For this simulation, we're mapping a 'service_name' to a direct port.
    """
    def __init__(self):
        # In a real K8s, 'service_a_name' would resolve to a ClusterIP
        # and then to a Pod IP via kube-proxy. Here, we map directly.
        self.services = {"service-a-cluster-ip": "127.0.0.1", "service-a-port": 8000}

    def resolve_service_endpoint(self, service_name_alias):
        """
        Resolves a 'service alias' to its simulated IP and port.
        """
        if service_name_alias == "service-a-cluster-ip":
            return self.services["service-a-cluster-ip"], self.services["service-a-port"]
        return None, None

def main():
    # Define ports for our simulated microservices
    SERVICE_A_PORT = 8000

    # Start Microservice A in a separate thread
    service_a_thread = threading.Thread(target=run_microservice_a, args=(SERVICE_A_PORT,))
    service_a_thread.daemon = True  # Allow the main program to exit even if this thread is running
    service_a_thread.start()

    # Give Microservice A a moment to start
    time.sleep(1)

    # Simulate Kubernetes Service discovery
    k8s_resolver = KubernetesServiceSimulator()
    resolved_host, resolved_port = k8s_resolver.resolve_service_endpoint("service-a-cluster-ip")

    if resolved_host and resolved_port:
        print(f"\n--- Simulating Kubernetes Service Discovery ---")
        print(f"Kubernetes resolved 'service-a-cluster-ip' to {resolved_host}:{resolved_port}")

        # Microservice B uses the "discovered" endpoint (as it would in K8s)
        microservice_b = MicroserviceB(resolved_host, resolved_port)
        response_from_b = microservice_b.call_service_a()
        print(f"{response_from_b}\n")
    else:
        print("Failed to resolve service-a-cluster-ip. Check KubernetesServiceSimulator.")

    # A more direct call simulation (if Service wasn't used)
    print("--- Direct call (without sophisticated Service discovery) ---")
    direct_microservice_b = MicroserviceB("127.0.0.1", SERVICE_A_PORT)
    direct_response = direct_microservice_b.call_service_a()
    print(f"{direct_response}")

    # Keep main thread alive for a bit to allow server threads to run
    time.sleep(2)
    print("\nSimulation complete.")

if __name__ == "__main__":
    main()
