# luxforge-logger.py
# Author: Luxforge
# Modular logging setup for Python applications

import socket
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os

class LuxforgeLogger:
    """
    LuxforgeLogger sets up a standardized logging configuration.
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
    # Standard logging levels, can be expanded if needed
    LEVELS = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
        "CHANGELOG": 25  # Custom level for changelog entries
    }


    def __init__(self, env_path="./config/global/logs.env"):
        # Initialize logger settings using environment variables
        
        # Set the node name and user
        self.node = socket.gethostname()
        self.user = os.getenv("USER") or os.getenv("USERNAME") or "unknown"

        # Set the version
        self.version_info = self.load_version()

        # Load environment variables from the specified .env file - puts them into os.environ
        load_dotenv(dotenv_path=env_path)

        # Read configuration from environment variables with defaults
        self.date_format = os.getenv("DATE_FORMAT", "%Y-%m-%d %H:%M:%S.%f")
        self.decimal_digits = int(os.getenv("NUMBER_OF_DIGITS_AFTER_DECIMAL", 3))

        # Set the log to file and console flags
        self._log_to_file = os.getenv("LOG_TO_FILE", "True").lower() == "true"
        self._log_to_console = os.getenv("LOG_TO_CONSOLE", "True").lower() == "true"

        # Set the log level
        level_str = os.getenv("LOGLEVEL", "DEBUG").upper()
        self.level = self.LEVELS.get(level_str, 10)
        
        # Initialize current task and log filename
        self._task = "init"

        # Set the base directory for logs
        self._log_dir = os.getenv("LOG_DIR", "./logs")
        self.base_dir = self._log_dir

        # Update the actual log directory
        self._update_directory()

        # Set the initial log filename
        self._update_filename()

        # Load max log size and backup settings
        self._max_log_size = int(os.getenv("MAX_LOG_SIZE_MB", 5))
        self._max_log_backup = int(os.getenv("MAX_LOG_BACKUP_COUNT", 5))

        # Post a log entry indicating initialization
        self.i(f"Logger initialized for node '{self.node}' by user '{self.user}'. Version: {self.version_info.get('version', 'unknown')}")
        self.i(f"Logging level set to {level_str} ({self.level})")

        # Show the current taskname
        self.task()


    def load_version(self, version_file="./version.yaml") -> dict:
        # Load version information from a YAML file
        import yaml
        try:
            with open(version_file, "r") as f:
                version_info = yaml.safe_load(f)
            return version_info
        except Exception as e:
            self.log(f"Failed to load version info: {e}", level="ERROR")
            return {}
    
    def _write(self, path, content, retries=3, timeout=1, encoding="utf-8"):
        for attempt in range(retries):
            try:
                with open(path, "a", encoding=encoding) as f:
                    f.write(content)
                return True
            except Exception as e:
                print(f"[luxforgeLogger] Write failed (attempt {attempt+1}): {e}")
                time.sleep(timeout)
        return False

    def _update_filename(self):

        # Set the timestamped log filename based on current task and time - it returns YYYYMMDD_HH00
        timestamp = datetime.now().strftime("%Y%m%d_%H00")

        # Update the log dir - just in case
        self._update_directory()

        # Create a safe task tag for the filename
        task_tag = self._task.replace(" ", "_") if self._task else "untagged"
        self.filename = os.path.join(self._log_dir, f"{task_tag}_{timestamp}.log")
    
    def _update_directory(self):

        # Rebuild the log directory path based on base_dir / task / yyyy / yyyy-mm / yyyy-mm-dd
        year_path = datetime.now().strftime("%Y")
        month_path = datetime.now().strftime("%Y-%m")
        day_path = datetime.now().strftime("%Y-%m-%d")
        date_path = os.path.join(year_path, month_path, day_path)
        self._log_dir = os.path.join(self.base_dir, self._task, date_path)

        # Ensure the log directory exists
        os.makedirs(self._log_dir, exist_ok=True)


    def task(self, task_name: str = None) -> str:
        # Method to set or get the current task name
        if task_name:
            self.i(f"Switching task from '{self._task}' to '{task_name}'")
            self._task = task_name
            # Update the filename to reflect the new task
            self._update_filename()
            self._update_directory()
        else:
            self.i(f"Set task to: {self._task}")
        return self._task
    
    def _formatted_timestamp(self) -> str:
        # Return the current timestamp formatted according to date_format and decimal_digits
        raw = datetime.now().strftime(self.date_format)
        if "%f" in self.date_format:
            split = raw.split(".")
            if len(split) == 2:
                micro = split[1][:self.decimal_digits]
                return f"{split[0]}.{micro}"
        return raw

    def log(self, message, level="INFO"):
        # General logging method - logs if level is >= current level
        if self.LEVELS.get(level.upper(), 0) >= self.level:
            self._log(message, level.upper())

    def _log(self, message, level):
        # Internal method to handle the actual logging

        # Set the timestamp formatted correctly
        timestamp = self._formatted_timestamp()
        node = self.node
        # Generate the log line
        line = f"[{timestamp}] [{node}] [{level}] {message}"

        # Log to file if enabled
        if self.log_to_file():

            # Ensure the filename is set and directory exists
            if not hasattr(self, 'filename'):
                self._update_filename()
            
            # Ensure the log directory exists
            Path(self.filename).parent.mkdir(parents=True, exist_ok=True)
            
            # Append the log line to the file
            self._write(self.filename, line + "\n", retries=5, timeout=1, encoding="utf-8")

        # Log to console if enabled
        if self.log_to_console():
            print(line)
    
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
        timestamp = self._formatted_timestamp()
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

    def max_log_size(self, size: int = None) -> int:
        # Method to set or get max log size in MB
        if size is not None:
            self._max_log_size = size
        return getattr(self, "_max_log_size", 5)  # Default to 5 MB if not set

    def max_log_backup(self, count: int = None) -> int:
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
            self._log_to_file = value
        return self._log_to_file

    def log_to_console(self, value: bool = None) -> bool:
        # Method to set or get log to console
        if value is not None:
            self._log_to_console = value
        return self._log_to_console

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



# Create a default logger instance for module-level use
logger = LuxforgeLogger()
luxforgeLogger = logger  # Alias for convenience