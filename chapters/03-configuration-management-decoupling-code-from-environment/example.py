# config_loader.py

import os

class ConfigurationLoader:
    """
    Loads application configuration, prioritizing environment variables,
    then a default dictionary, simulating ConfigMaps/Secrets.
    """

    DEFAULT_SETTINGS = {
        "DATABASE_HOST": "localhost",
        "DATABASE_PORT": "5432",
        "API_KEY": "default_api_key_for_dev", # Simulate a default secret
        "FEATURE_TOGGLE_A": "true",
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, prefix="APP_"):
        """
        Initializes the configuration loader.
        Args:
            prefix (str): Prefix for environment variables to look for.
        """
        self._prefix = prefix
        self._config = self._load_config()

    def _load_config(self):
        """
        Loads configuration from environment variables, falling back to defaults.
        """
        config = self.DEFAULT_SETTINGS.copy()

        # Iterate through default settings to find corresponding environment variables
        for key, default_value in self.DEFAULT_SETTINGS.items():
            env_var_name = f"{self._prefix}{key}" # e.g., APP_DATABASE_HOST
            if env_var_name in os.environ:
                config[key] = os.environ[env_var_name]
                print(f"Loaded config '{key}' from environment variable '{env_var_name}'")
            else:
                print(f"Using default config '{key}': '{default_value}'")

        return config

    def get(self, key, default=None):
        """
        Retrieves a configuration value.
        Args:
            key (str): The configuration key.
            default: Default value if key is not found (shouldn't happen with current _load_config).
        Returns:
            The configuration value.
        """
        return self._config.get(key, default)

# --- Application Entry Point (simulated) ---
if __name__ == "__main__":
    print("--- Simulating application startup ---")

    # Scenario 1: No environment variables set (uses defaults)
    print("\n--- Scenario 1: Default configuration ---")
    app_config = ConfigurationLoader()
    print(f"DB Host: {app_config.get('DATABASE_HOST')}")
    print(f"API Key: {app_config.get('API_KEY')}") # Shows default secret
    print(f"Feature A Enabled: {app_config.get('FEATURE_TOGGLE_A')}")

    # Scenario 2: Environment variables inject new configuration (like ConfigMap/Secret)
    print("\n--- Scenario 2: Configuration injected via environment variables ---")
    os.environ["APP_DATABASE_HOST"] = "production-db.example.com"
    os.environ["APP_API_KEY"] = "super_secret_prod_key_123" # Simulating a Secret injection
    os.environ["APP_FEATURE_TOGGLE_A"] = "false"
    os.environ["APP_SERVICE_ACCOUNT_EMAIL"] = "sa@example.com" # New config

    app_config_prod = ConfigurationLoader()
    print(f"DB Host: {app_config_prod.get('DATABASE_HOST')}")
    print(f"API Key: {app_config_prod.get('API_KEY')}") # Shows injected secret
    print(f"Feature A Enabled: {app_config_prod.get('FEATURE_TOGGLE_A')}")
    print(f"Service Account (new config): {app_config_prod.get('SERVICE_ACCOUNT_EMAIL', 'not_set')}")

    # Clean up environment variables
    del os.environ["APP_DATABASE_HOST"]
    del os.environ["APP_API_KEY"]
    del os.environ["APP_FEATURE_TOGGLE_A"]
    del os.environ["APP_SERVICE_ACCOUNT_EMAIL"]

    print("\n--- End of simulation ---")
