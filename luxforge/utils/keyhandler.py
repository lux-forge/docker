# /#! /usr/bin/env python3

# keyhandler.py
# Author: Luxforge
# Utility to handle keypresses in the terminal

from utils.logger import logger

class KeyHandler:
    """
    Handle keypresses in the terminal, including special keys.
    """

    def __init__(self):
        import termios, tty, sys
        # Store the imported modules as instance variables
        self.termios = termios # termios module for terminal I/O
        self.tty = tty # tty module for terminal control
        self.sys = sys # sys module for system operations
        self.typed = "" # Store typed characters

    def get_key(self):
        # Read a single keypress from stdin and return it
        # Set terminal to raw mode to capture keypresses directly

        # Get the file descriptor for stdin
        fd = self.sys.stdin.fileno()

        # Save the current terminal settings
        old = self.termios.tcgetattr(fd)

        # Set terminal to raw mode
        try:
            self.tty.setraw(fd)
            
            # Read a single character
            ch1 = self.sys.stdin.read(1)
            
            # Handle escape sequences for special keys
            if ch1 == '\x1b':
                ch2 = self.sys.stdin.read(2)
                return ch1 + ch2
            
            # Return the single character for regular keys
            return ch1
        
        # Restore the original terminal settings
        finally:
            self.termios.tcsetattr(fd, self.termios.TCSADRAIN, old)

    def interpret(self, raw_key):
        """
        Interpret the raw key input and return a standardized representation.
        PARAM raw_key: The raw key input from get_key()
        """
        logger.debug(f"Interpreting raw key: {raw_key}")
        mapping = {
            '\x1b[A': 'UP',
            '\x1b[B': 'DOWN',
            '\x1b[C': 'RIGHT',
            '\x1b[D': 'LEFT',
            '\n': 'ENTER',
            '\r': 'ENTER',
            '\x7f': 'BACKSPACE',
            '\x1b': 'ESC'
        }

        # Full alphabet mapping
        if len(raw_key) == 1 and raw_key.isalpha():
            logger.debug(f"Alphabetic key detected: {raw_key}")
            return raw_key.upper()

        # Digit passthrough
        if len(raw_key) == 1 and raw_key.isdigit():
            logger.debug(f"Digit key detected: {raw_key}")
            return raw_key

        # Return mapped value or the raw key if not found
        mapped_key = mapping.get(raw_key, raw_key)

        if mapped_key == raw_key:
            logger.debug(f"No mapping found for key: {raw_key}. Returning raw key.")
        else:
            logger.debug(f"Mapped key: {raw_key} -> {mapped_key}")
        return mapped_key

    def reset(self):
        self.typed = ""

    def get_typed(self):
        return self.typed