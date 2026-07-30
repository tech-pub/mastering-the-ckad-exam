# This script simulates a Kubernetes-like event stream and demonstrates a basic
# event analysis to identify potential issues with a 'pod' resource.

import time
import random

def generate_event(resource_type, resource_name, event_type, reason, message):
    """
    Generates a dictionary representing a Kubernetes-like event.
    """
    return {
        "timestamp": time.time(),
        "resourceType": resource_type,
        "resourceName": resource_name,
        "eventType": event_type,  # e.g., Normal, Warning
        "reason": reason,         # e.g., Scheduled, FailedAttachVolume, ErrImagePull
        "message": message
    }

def analyze_events(events):
    """
    Analyzes a list of events to identify common troubleshooting patterns.
    """
    critical_events = []
    pod_states = {} # Track the last known state for pods
    network_policy_issues = []

    for event in events:
        resource_type = event["resourceType"]
        resource_name = event["resourceName"]
        event_type = event["eventType"]
        reason = event["reason"]
        message = event["message"]

        # Example 1: Pod stuck in pending/unready due to resource issues
        if resource_type == "pod":
            if event_type == "Warning" and reason in ["FailedScheduling", "Evicted"]:
                critical_events.append(f"CRITICAL: Pod '{resource_name}' - {reason}: {message}")
            elif event_type == "Warning" and "ErrImagePull" in reason:
                critical_events.append(f"CRITICAL: Pod '{resource_name}' - Image Pull Error: {message}")
            elif reason == "FailedAttachVolume" or "volume" in message.lower():
                critical_events.append(f"WARNING: Pod '{resource_name}' - Volume Issue: {message}")

            # Basic state tracking (simplified)
            if reason == "Scheduled":
                pod_states[resource_name] = "scheduled"
            elif reason == "Pulled" or reason == "Created":
                pod_states[resource_name] = "running"
            elif reason == "Failed":
                pod_states[resource_name] = "failed"

        # Example 2: Network policy issues (inferred from connection failures or denied messages)
        # This is highly simplified as real network policy issues are harder to detect from events alone
        if "network policy" in message.lower() or "connection refused" in message.lower():
            network_policy_issues.append(f"POSSIBLE NETWORK POLICY ISSUE: {message} for {resource_type}/{resource_name}")

    if not critical_events and not network_policy_issues:
        critical_events.append("No immediate critical issues detected in the event stream.")

    return critical_events, network_policy_issues

# --- Simulation ---
event_stream = []

# Simulate normal pod lifecycle events
event_stream.append(generate_event("pod", "my-app-pod-1", "Normal", "Scheduled", "Successfully assigned my-app-pod-1 to node-1"))
event_stream.append(generate_event("pod", "my-app-pod-1", "Normal", "Pulling", "Pulling image 'nginx:latest'"))
event_stream.append(generate_event("pod", "my-app-pod-1", "Normal", "Pulled", "Successfully pulled image 'nginx:latest'"))
event_stream.append(generate_event("pod", "my-app-pod-1", "Normal", "Created", "Created container nginx"))
event_stream.append(generate_event("pod", "my-app-pod-1", "Normal", "Started", "Started container nginx"))

# Simulate a problem: image pull error for another pod
event_stream.append(generate_event("pod", "my-app-pod-2", "Warning", "ErrImagePull", "Failed to pull image 'nonexistent-app:v1'"))
event_stream.append(generate_event("pod", "my-app-pod-2", "Warning", "Failed", "Error: ImagePullBackOff"))

# Simulate a network policy issue (inferred from a generic message)
event_stream.append(generate_event("deployment", "backend-deploy", "Warning", "FailedConnection", "Connection to database pod was refused. Check network policy."))


# Analyze the simulated events
print("--- Analyzing Event Stream ---")
issues, net_policy_issues = analyze_events(event_stream)

print("\n--- Detected Critical Issues ---")
for issue in issues:
    print(issue)

print("\n--- Suspected Network Policy Issues ---")
for issue in net_policy_issues:
    print(issue)

# Expected output demonstrates how a "senior" engineer might correlate events
# beyond simple log messages to infer deeper problems like image pull issues
# or potential network policy misconfigurations.
