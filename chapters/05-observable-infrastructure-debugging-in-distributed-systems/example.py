import logging
import time
import random
from datetime import datetime

# --- Log Aggregation Setup ---
# Configure logging to output to console, simulating aggregation
# In a real distributed system, this would be collected by a log agent (e.g., Fluentd, Filebeat)
# and sent to a central logging system (e.g., Elasticsearch, Loki).
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('distributed-service')

# --- Health Probe Configuration (Simulated) ---

def simulate_external_dependency_check():
    """
    Simulates checking an external dependency's health.
    Could be a database, another microservice, message queue, etc.
    """
    # Introduce random failures to simulate real-world scenarios
    if random.random() < 0.2:  # 20% chance of failure
        logger.error("Health probe critical: External database connection failed!")
        return False
    logger.info("Health probe OK: External database connection healthy.")
    return True

def simulate_resource_availability_check():
    """
    Simulates checking internal resource availability (e.g., CPU, Memory, Queue size).
    """
    current_load = random.randint(0, 100)
    if current_load > 80:  # Simulate high load
        logger.warning(f"Health probe warning: High internal load detected: {current_load}% CPU usage.")
        return False  # Or return True but indicate degraded performance
    logger.info(f"Health probe OK: Internal resources within limits. CPU usage: {current_load}%.")
    return True

def main_service_logic():
    """
    Simulates the core logic of a distributed service.
    This function would perform actual work using dependencies.
    """
    logger.info("Service: Starting processing unit.")
    try:
        # Simulate a task that might fail
        if random.random() < 0.1: # 10% chance of an internal error
            raise ValueError("Simulated unexpected internal error during processing!")

        time.sleep(random.uniform(0.1, 0.5)) # Simulate work
        logger.debug("Service: Processing unit completed successfully.") # Use debug for fine-grained logs
    except ValueError as e:
        logger.exception(f"Service: Critical error during processing: {e}")
        return False
    return True

# --- Main simulation loop ---
if __name__ == "__main__":
    logger.info("Distributed Service Simulator starting...")
    for i in range(1, 11): # Simulate 10 service cycles
        logger.info(f"\n--- Cycle {i} at {datetime.now()} ---")

        # Periodically check health probes
        dependency_ok = simulate_external_dependency_check()
        resource_ok = simulate_resource_availability_check()

        if not dependency_ok:
            logger.critical("Service cannot proceed due to critical external dependency failure.")
            # In a real system, this might trigger an alert or a restart
            time.sleep(1) # Pause before next cycle to allow for manual intervention or restart
            continue
        if not resource_ok:
            logger.warning("Service operating under degraded conditions due to resource constraints.")
            # Service might still process but with warnings

        # Execute main service logic only if core dependencies are met
        if main_service_logic():
            logger.info("Service: Cycle completed successfully.")
        else:
            logger.error("Service: Cycle failed due to internal error.")

        time.sleep(0.5) # Short delay between cycles

    logger.info("\nDistributed Service Simulator stopped.")
