"""
Logging configuration module.
This module sets up the logging configuration for the application.
"""

import os  # Standard imports should be listed first
import logging
import logging.config
import yaml

def setup_logging(
    default_path='config/log_config.yaml',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Setup logging configuration.
    Loads the logging configuration from a YAML file if available, 
    otherwise sets up a basic logging configuration.

    Args:
        default_path (str): Path to the default logging configuration file.
        default_level (int): Default logging level if no configuration is provided.
        env_key (str): Environment variable that points to the logging configuration file.
    """
    path = default_path

    # Check if an environment variable is set to override the config path
    value = os.getenv(env_key, None)
    if value:
        path = value

    # Load logging configuration from the YAML file if it exists
    if os.path.exists(path):
        with open(path, 'rt', encoding='utf-8') as file:  # Specify encoding explicitly
            try:
                config = yaml.safe_load(file.read())
                logging.config.dictConfig(config)
            except Exception as exception:  # Use a more descriptive name than "e"
                print(f"Error in logging configuration file: {exception}")
                logging.basicConfig(level=default_level)
    else:
        # Fallback to basic configuration if the file doesn't exist
        logging.basicConfig(level=default_level)
        print(f"Logging configuration file not found: {path}")

# Initialize the logger
logger = logging.getLogger(__name__)
setup_logging()
