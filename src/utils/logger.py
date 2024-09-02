"""
Sets up logging configuration from a YAML file. If the file is not found or
there's an error in the configuration, it falls back to a basic logging configuration.
"""

import os
import logging
import logging.config
import yaml  # pylint: disable=import-error

def setup_logging(default_path: str = '~/.mrpir/config/log_config.yaml',
                  default_level: int = logging.INFO) -> None:
    """
    Sets up logging configuration from a YAML file. If the file is not found or
    there's an error in the configuration, it falls back to a basic logging configuration.

    Args:
        default_path (str): The default path to the logging configuration YAML file.
        default_level (int): The default logging level to use if the configuration 
        file is not found or invalid.
    """
    # Define the log directory within the user's home directory
    log_dir = os.path.expanduser('~/.mrpir/logs')

    # Ensure the log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Adjust the path to the logging configuration file, expanding user directory
    config_path = os.path.expanduser(default_path)

    if os.path.exists(config_path):
        with open(config_path, 'rt', encoding='utf-8') as file:
            try:
                config = yaml.safe_load(file.read())
                if config is not None:
                    # Dynamically update the logfile path in the configuration
                    for handler in config.get('handlers', {}).values():
                        if 'filename' in handler:
                            handler['filename'] = os.path.join(log_dir, os.path.basename(handler['filename']))
                    
                    logging.config.dictConfig(config)
                else:
                    raise ValueError("Loaded YAML configuration is empty.")
            except yaml.YAMLError as err:
                print(f"Error parsing YAML file: {err}")
                logging.basicConfig(level=default_level)
    else:
        print(f"Logging configuration file not found: {config_path}")
        logging.basicConfig(level=default_level)

# Initialize the logger and set up logging configuration
logger = logging.getLogger(__name__)
setup_logging()
