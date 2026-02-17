"""
Simple logger for PayWatch.
"""
import logging
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)


def setup_logger(name="paywatch", level=logging.INFO):
    """
    Create a logger with colored output.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    
    # Create formatter with colors
    class ColoredFormatter(logging.Formatter):
        """Custom formatter with colors"""
        
        COLORS = {
            'DEBUG': Fore.MAGENTA,
            'INFO': Fore.CYAN,
            'WARNING': Fore.YELLOW,
            'ERROR': Fore.RED,
            'CRITICAL': Fore.RED + Style.BRIGHT,
        }
        
        def format(self, record):
            # Add color to level name
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
            
            return super().format(record)
    
    # Set format
    formatter = ColoredFormatter(
        fmt='[%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(handler)
    
    return logger


# Create default logger
logger = setup_logger()