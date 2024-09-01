"""
Sets up logging configuration from a YAML file. If the file is not found or
there's an error in the configuration, it falls back to a basic logging configuration.
"""

import os
import logging
import logging.config
import yaml  # pylint: disable=import-error


def setup_logging(default_path: str = '../config/log_config.yaml',
                  default_level: int = logging.INFO) -> None:
    """
    Sets up logging configuration from a YAML file. If the file is not found or
    there's an error in the configuration, it falls back to a basic logging configuration.

    Args:
        default_path (str): The default path to the logging configuration YAML file.
        default_level (int): The default logging level to use if the configuration 
        file is not found or invalid.
    """
    # Adjust the path relative to the script's location
    base_path = os.path.dirname(os.path.dirname(__file__))  # Go up one directory from utils
    path = os.path.join(base_path, default_path)

    if os.path.exists(path):
        with open(path, 'rt', encoding='utf-8') as file:
            try:
                config = yaml.safe_load(file.read())
                if config is not None:
                    logging.config.dictConfig(config)
                else:
                    raise ValueError("Loaded YAML configuration is empty.")
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file: {e}")
                logging.basicConfig(level=default_level)
    else:
        print(f"Logging configuration file not found: {path}")
        logging.basicConfig(level=default_level)


# Initialize the logger and set up logging configuration
logger = logging.getLogger(__name__)
setup_logging()
