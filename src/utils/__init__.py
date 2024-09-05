"""
Init file for the utils package.
"""

# Importing utility modules to make them available when the package is imported
from .logger import LoggerManager, ExcludeSystemdNotifierFilter

# Defining what is available in the package's namespace
__all__ = ['LoggerManager', 'ExcludeSystemdNotifierFilter']


# Example usage in another file:
# from utils import LoggerManager
