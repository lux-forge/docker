# /#!/usr/bin/env python3

# # logger.py
# Author: Luxforge
# Modular logging setup for Python applications

import socket
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from time import sleep
from utils.pathloader import paths
import os

from utils.colours import Colours

class Logger:
    """
    Logger sets up a standardized logging configuration.
    ARGS:
        name: Logger name (default: "luxforge")
        log_to_file: Whether to log to a file (default: False)
        log_dir: Directory to store log files (default: "./logs")
        level: Logging level (default: logging.INFO)
    METHODS:
        info(msg): Log an info message
        warning(msg): Log a warning message
        error(msg): Log an error message
        debug(msg): Log a debug message
        exception(msg): Log an exception message
    PROPERTIES:
        logger: The underlying logging.Logger instance
    """
    # Standard logging levels, can be expanded if needed - add colours 
    LEVELS = {
        "DEBUG": (10, "gray"),
        "INFO": (20, None),
        "CHANGELOG": (25, "blue"),  # Custom level for changelog entries
        "WARNING": (30, "yellow"),
        "ERROR": (40, "orange"),
        "CRITICAL": (50, "red")
    }

    def __init__(self, env_path=f"{paths.config}/global/logs.env"):
        # Initialize logger settings using environment variables
        
        # Set the node name and user
        self.node = socket.gethostname()
        self.user = os.getenv("USER") or os.getenv("USERNAME") or "unknown"

        # Set the version
        self.version_info = self.__load_version()

        # Load environment variables from the specified .env file - puts them into os.environ
        load_dotenv(dotenv_path=env_path)

        # Initialize current task and log filename
        self.task = "init"
        
        # Set the base directory for logs
        self.log_dir = os.getenv("LOG_DIR", paths.logs)
        self.base_dir = self.log_dir

        # Read configuration from environment variables with defaults
        self.date_format = os.getenv("DATE_FORMAT", "%Y-%m-%d %H:%M:%S.%f")
        self.decimal_digits = int(os.getenv("NUMBER_OF_DIGITS_AFTER_DECIMAL", 3))

        # Set the log to file and console flags
        self.__log_to_file = os.getenv("LOG_TO_FILE", "True").lower() == "true"
        self.__log_to_console = os.getenv("LOG_TO_CONSOLE", "True").lower() == "true"

        # Set the log level
        level_int = int( os.getenv("LOGLEVEL", "DEBUG"))
        self.__level(level_int)

        # Update the actual log directory
        self.__update_directory()

        # Set the initial log filename
        self.__update_filename()
        
        # Load max log size and backup settings
        self.__max_log_size(int(os.getenv("MAX_LOG_SIZE_MB", 5)))
        self.__max_log_backup(int(os.getenv("MAX_LOG_BACKUP_COUNT", 5)))

        # Post a log entry indicating initialization
        self.i(f"Logger initialized for node '{self.node}' by user '{self.user}'. Version: {self.version_info.get('version', 'unknown')}")
        self.i(f"Logging level set to {level_int} ({self.level})")

        # Show the current taskname
        self.__task()

    def __load_version(self, version_file=f"{paths.root}/version.yaml") -> dict:
        # Load version information from a YAML file
        import yaml
        try:
            with open(version_file, "r") as f:
                version_info = yaml.safe_load(f)
            return version_info
        except Exception as e:
            self.log(f"Failed to load version info: {e}", level="ERROR")
            return {}
    
    def __write(self, path, content, retries=3, timeout=1, encoding="utf-8"):
        for attempt in range(retries):
            try:
                with open(path, "a", encoding=encoding) as f:
                    f.write(content)
                return True
            except Exception as e:
                print(f"[luxforgeLogger] Write failed (attempt {attempt+1}): {e}")
                sleep(timeout)
        return False

    def __update_filename(self):

        # Set the timestamped log filename based on current task and time - it returns YYYYMMDD_HH00
        timestamp = datetime.now().strftime("%Y%m%d_%H00")

        # Update the log dir - just in case
        self.__update_directory()

        # Create a safe task tag for the filename
        task_tag = self.task.replace(" ", "_") if self.task else "untagged"
        self.filename = os.path.join(self.log_dir, f"{task_tag}_{timestamp}.log")
    
    def __update_directory(self):

        # Rebuild the log directory path based on base_dir / task / yyyy / yyyy-mm / yyyy-mm-dd
        year_path = datetime.now().strftime("%Y")
        month_path = datetime.now().strftime("%Y-%m")
        day_path = datetime.now().strftime("%Y-%m-%d")
        date_path = os.path.join(year_path, month_path, day_path)
        self.log_dir = os.path.join(self.base_dir, self.task, date_path)

        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

    def __task(self, task_name: str = None) -> str:
        # Method to set or get the current task name
        if task_name:
            self.i(f"Switching task from '{self.task}' to '{task_name}'")
            self.task = task_name
            # Update the filename to reflect the new task
            self.__update_filename()
            self.__update_directory()
        else:
            self.i(f"Set task to: {self.task}")
        return self.task

    def __formatted_timestamp(self) -> str:
        # Return the current timestamp formatted according to date_format and decimal_digits
        raw = datetime.now().strftime(self.date_format)
        if "%f" in self.date_format:
            split = raw.split(".")
            if len(split) == 2:
                micro = split[1][:self.decimal_digits]
                return f"{split[0]}.{micro}"
        return raw

    def log(self, message, level: str = None):
        # General logging method - logs if level is >= current level
        if level is None:
            level = "INFO" # Default to INFO if no level provided
        else:
            level = level.upper()
            if level not in self.LEVELS:
                level = "INFO"  # Default to INFO if unknown level
        level_int = self.LEVELS[level][0]

        # General logging method - logs if level is >= current level
        if level_int >= self.level[0]:
            self.__log(message, level)

    def __log(self, message: str = None, level: str = "INFO"):
        # Internal method to handle the actual logging
        level = level.upper()
        if level not in self.LEVELS:
            level = "INFO"  # Default to INFO if unknown level

        # Set the timestamp formatted correctly
        timestamp = self.__formatted_timestamp()
        node = self.node

        # Generate the log line
        line = f"[{timestamp}] [{node}] [{level}] {message}"

        # Log to file if enabled
        if self.log_to_file():

            # Ensure the filename is set and directory exists
            if not hasattr(self, 'filename'):
                self.__update_filename()
            
            # Ensure the log directory exists
            Path(self.filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Append the log line to the file
            self.__write(self.filename, line + "\n", retries=5, timeout=1, encoding="utf-8")

        # Log to console if enabled
        if self.log_to_console():
            # Get the colour
            colour = self.LEVELS[level][1]
            
            # If its critical, make it bold
            if level == "CRITICAL":
                line = Colours.colour_text(line, colour, bold=True)
            else:
                line = Colours.colour_text(line, colour)
            print(line)

    def __find_by_level(self, int_level: int = 20) -> str:
        # Using the level numeric, return the key name. Default to INFO if not found
        return next((k for k, v in self.LEVELS.items() if v[0] == int_level), "INFO")

    def __level(self, level) -> None:
        # Getter and Setter for log level

        # Level can be a string, int, tuple or none
        if isinstance(level, int):
            # Set the log level directly if it's an int - defaults to info if unknown
            key = self.__find_by_level(level)
            self.level = self.LEVELS.get(key, self.LEVELS["INFO"])
        
        elif isinstance(level, tuple) and len(level) == 2:
            # Set the log level directly if it's a tuple (int, colour)
            self.level = level

        elif isinstance(level, str):
            # Set the log level by name if it's a string
            self.level = self.LEVELS.get(level.upper(), self.LEVELS["INFO"])

        elif level is None:
            # Set the level to default if nothing requested
            self.level = self.LEVELS["INFO"]
        
        # Show the current level
        self.i(f"Log level set to {self.level} ({self.__find_by_level(self.level[0])})")

        return self.level
        
    # INFO level logging method
    def info(self, message):
        self.log(message, level="INFO")
    i = info # Alias for info
    inf = info # Alias for info
    information = info # Alias for info
    
    # WARNING level logging method
    def warning(self, message):
        self.log(message, level="WARNING")
    warn = warning # Alias for warning
    w = warning # Alias for warning

    # ERROR level logging method
    def error(self, message):
        self.log(message, level="ERROR")
    err = error # Alias for error
    e = error # Alias for error
    exception = error # Alias for error
    exc = error # Alias for error
    ex = error # Alias for error

    # DEBUG level logging method
    def debug(self, message):
        self.log(message, level="DEBUG")
    dbg = debug # Alias for debug
    d = debug # Alias for debug
    
    # CRITICAL level logging method
    def critical(self, message):
        self.log(message, level="CRITICAL")
    crit = critical # Alias for critical
    c = critical # Alias for critical

    # CHANGELOG level logging method
    def emit_changelog(self, event: str, context: dict = None):
        """
        Emit a structured changelog entry to the current log file.

        ARGS:
            event (str): Description of the event (e.g. "etcd quorum joined", "version bump")
            context (dict): Optional metadata (e.g. {"version": "1.3.7", "node": "MARTEL"})
        """
        timestamp = self.__formatted_timestamp()
        node = self.node
        task = "changelog"
        version = self.version_info.get("version", "unknown")

        # Build changelog line
        line = f"[version:{version}] {event}"
        if context:
            meta = " ".join([f"{k}:{v}" for k, v in context.items()])
            line += f" | {meta}"

        # Log it
        self.log(line, level="CHANGELOG")
    changelog = emit_changelog
    ch = emit_changelog
    cl = emit_changelog

    def __max_log_size(self, size: int = None) -> int:
        # Method to set or get max log size in MB
        if size is not None:
            self._max_log_size = size
        return getattr(self, "_max_log_size", 5)  # Default to 5 MB if not set

    def __max_log_backup(self, count: int = None) -> int:
        # Method to set or get max log backup count
        if count is not None:
            self._max_log_backup = count
        return getattr(self, "_max_log_backup", 5)  # Default to 5 backups if not set

    def archive_old_logs(self):
        # Method to archive old logs
        pass

    def clear_old_logs(self, days: int):
        # Method to clear logs older than X days
        pass

    def log_to_file(self, value: bool = None) -> bool:
        # Method to set or get log to file
        if value is not None:
            self.__log_to_file = value
        return self.__log_to_file

    def log_to_console(self, value: bool = None) -> bool:
        # Method to set or get log to console
        if value is not None:
            self.__log_to_console = value
        return self.__log_to_console

    def log_level(self, level: str = None) -> int:
        
        # Method to set or get log level
        if level and level.upper() in self.LEVELS:
            self.level = self.LEVELS[level.upper()]
        return self.level
    
    def date_format(self, fmt: str = None) -> str:
        # Method to get or set the date format
        if fmt:
            self.date_format = fmt
        return self.date_format
    
    def decimal_digits(self, digits: int = None) -> int:
        # Method to get or set the number of decimal digits
        if digits is not None:
            self.decimal_digits = digits
        return self.decimal_digits
    
    def test_logger_levels(self):
        timestamp = self.__formatted_timestamp()
        node = self.node
        task = "test_logger_levels"
        self.i(f"Testing logger levels at {timestamp} on node {node} for task {task}")
        self.__task(task)
        self.i(f"Current log level set to {self.level}")
        self.level = self.LEVELS["DEBUG"]
        self.info("This is an info message.")
        self.warning("This is a warning message.")
        self.error("This is an error message.")
        self.debug("This is a debug message.")
        self.critical("This is a critical message.")
        self.emit_changelog("Version bump", {"version": "1.0.1", "node": self.node})
        
# Create a default logger instance for module-level use
logger = Logger()

if __name__ == "__main__":
    # Test the logger functionality
    print("[INFO] Testing luxforgeLogger functionality...")
    luxforgeLogger = Logger()
    luxforgeLogger.test_logger_levels()