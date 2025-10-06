#!/usr/bin/env python3

# menu.py
# Author: Luxforge
# Abstracted menu class for Luxforge tools

import datetime
import shutil
import sys, os
from abc import ABC

# Load the other luxforge classes and functions
from utils.logger import logger
from utils.colours import Colours
from utils.keyhandler import KeyHandler

class Menu(ABC):
    """
    Abstracted CLI menu for management tasks.
    """

    # Static options though they can be modified if necessary
    width = shutil.get_terminal_size((80, 20)).columns
    exit_options = ["X", "EXIT", "QUIT", "Q", None,""]
    back_options = ["B", "BACK", "RETURN","<","<<","PREVIOUS"]
    default_negative = ["N", "NO", "0", "FALSE", "F",None,""]
    default_positive = ["Y", "YES", "1", "TRUE", ""]
    
    # Default options - subclasses should override this
    options = {
        # Dictionary to hold menu options and their corresponding functions
        # Note that exit and back options are added automatically
        "1": ("option 1", "example_method_1"),
        "A": ("option A", "example_method_A")
    } 
    menu_name = "Base Menu"
    colours = {
        "title_border": "DEEP_MAGENTA",
        "title_info": "gray",
        "title": "DEEP_MAGENTA",
        "option": "white",
        "input_prompt": "cyan",
        "options_border": "gray"
    }
    border = {
        "top_left": "┌",
        "top_right": "┐",
        "bottom_left": "└",
        "bottom_right": "┘",
        "horizontal": "─",
        "vertical": "│",
        "space": " ",
        "title_space": " ",
        "title_margin": 2,
        "title_colour": "DEEP_MAGENTA",
        "option_colour": "gray",
        "options_margin": 3
    }

    def __init__(self, selected_option: str = None, previous_menu: str = None):
        """
        Initialize the menu with optional selected option and previous menu.
        PARAM: selected_option - Option to launch directly, if None, show menu
               previous_menu - Previous menu instance, if any
        """
        # Ensure that subclasses override the options dict
        if self.__class__ == Menu or self.options == Menu.options:
            logger.error(f"{self.__class__.__name__} must override static 'options' dict")
            raise NotImplementedError(f"{self.__class__.__name__} must override static 'options' dict")

        # Set the main variables used by all subclasses
        self.selected_option = selected_option

        # Set the previous menu - used for returning to previous menu if needed
        self.previous_menu = previous_menu

        # Generate a callable list of valid options for user input validation
        self.valid_options_as_list = list(self.options.keys())

        # if there is a previous menu, add back options to valid options
        if self.previous_menu:
            self.valid_options_as_list += self.back_options
            # Add back option to options dict if not already present
            for back_option in self.back_options:
                if back_option not in self.options:
                    self.options["B"] = (f"Back to {self.previous_menu.menu_name}", "return_to_previous_menu")

        # Add exit options to valid options
        self.valid_options_as_list += self.exit_options

        # Add exit option to options dict
        self.options["X"] = ("Exit Menu", "exit_menu")

        # Generate a string of valid options for user input prompts
        self.valid_options_as_str = self.__clean_list_to_str(self.options.keys())
        self.exit_options_as_str = self.__clean_list_to_str(self.exit_options)

        # Set up a key handler
        self.key_handler = KeyHandler()
        
        # Load the setup script path - load can accept args to launch directly into functions
        if selected_option:
            self.launch(selected_option)

    def example_method_1(self):
        # Example method for option 1
        self.__print("[+] Example method 1 called", "blue")
        input("Press Enter to continue...")

    def example_method_A(self):
        # Example method for option A
        self.__print("[+] Example method A called", "blue")
        input("Press Enter to continue...")

    def launch(self, selected_option: str = None):
        """
        Callable entry point for the menu
        PARAM: selected_option - Option to launch directly, if None, show menu
        """

        # Begin the menu loop
        while True:
            # If we have a selected option, validate and launch it
            if selected_option:
                self.__handle_option(selected_option)
            else:
                self.__show_menu(self.options)

    def __show_menu(self, options: dict = None):
        """
        Display the options as a menu with a header
        PARAM: options - Dictionary of options to display. Can be overridden by subclasses.
        """
        
        # Clear screen
        self.__clear()

        # Generate header
        self.__generate_header()
       # Display options - add a gap before back/exit options
        for key, (desc, method_name) in options.items():
           if key in self.back_options:
               self.__boxify_middle(text="", type="options_space") # Add a blank line before back options
           elif key in self.exit_options:
               self.__boxify_middle(text="", type="options_space") # Add a blank line before exit options
           self.__boxify_middle(text=f"{key}  |  {desc}", type="option")

        self.__boxify_middle(text="", type="options_space") # Add a blank line after options
        self.__boxify_top_bottom(title=False, top=False) # Bottom border
        
        # Request user input - strip whitespace and convert to uppercase
        choice = self.__interactive_select(options)

        # Validate input
        valid_input = self.__validate_user_input(choice)

        # If valid, handle the option by passing to the called function
        if valid_input:
            self.__handle_option(valid_input)

    def __handle_option(self, option: str):
        """
        Handles the selected option by calling the corresponding method
        PARAM: option - The selected option to handle
        """

        # Get the method name from the options dict
        method_name = self.options[option][1]

        # Get the method from the class
        method = getattr(self, method_name, None)

        # If the method exists and is callable, call it
        if callable(method):
            logger.info(f"Launching option '{option}': {self.options[option][0]}")
            method()
        else:
            self.__print(f"[!] Method '{method_name}' for option '{option}' is not implemented.", "red")
            input("Press Enter to continue...")
        
    def __print(self, message, colour=None, bold=False, underline=False, reverse=False):
        # Using colours module for coloured output
        print(Colours.colour_text(message, colour=colour, bold=bold, underline=underline, reverse=reverse))

    def __validate_user_input(self, choice):
        """
        Ensures user input is valid
        PARAM: choice - User input to validate
        RETURNS: Validated choice or exits if quit option
        """
    
        # Convert input to uppercase and strip whitespace and into a string
        try:
            choice = str(choice).upper().strip()
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            input("Press Enter to continue...")
            return False
        
        # Combine valid and quit options
        all_options = self.valid_options_as_list + self.exit_options

        # Validate user input against a list of valid options
        logger.debug(f"Validating user input: {choice} against options: {all_options}")

        if choice not in all_options:
            print(f"[!] Invalid input. Please choose from: ({self.valid_options_as_str}) to proceed or ({self.exit_options_as_str}) to exit.", "red")
            input("Press Enter to continue...")
            return False
        
        # Quit if in quit options
        if choice in self.exit_options:
            self.__print("[+] Exiting menu.", "gray")
            sys.exit(0)

        # Return the value if valid
        logger.debug(f"User input '{choice}' is valid.")
        
        # Pause only when in debug mode to allow for faster navigation in normal use
        if logger.level == 10: # DEBUG
            input("Press Enter to continue...")
        return choice

    def __confirm_action(self, negative_options: list = None, positive_options: list = None, prompt: str = "[?] Are you sure? (Y/n) or X to exit: "):
        """
        Confirm an action with the user
        PARAM:  negative_options - List of options to consider as negative.
                positive_options - List of options to consider as positive. 
                prompt - Prompt to display to the user
        """

        # Refine options to remove duplicates and normalize to lowercase
        negative_options = self.__refine_confirm_options(negative_options, type="negative")
        positive_options = self.__refine_confirm_options(positive_options, type="positive")

        # Set a local version of the default exit options if any are in negative options, remove them from exit options
        # This prevents accidental exits when user is trying to say no
        # e.g. if negative_options includes 'q', remove 'q' from exit options
        if any(opt in self.exit_options for opt in negative_options):
            exit_options = [opt for opt in self.exit_options if opt not in negative_options]
        else:
            exit_options = self.exit_options

        # If any of negative in positive_options or vice versa, throw error and remove from both
        intersection = set(negative_options).intersection(set(positive_options))
        if intersection:
            logger.warning(f"Conflicting options in confirm_action: {intersection}. Removing from both lists.")
            negative_options = [opt for opt in negative_options if opt not in intersection]
            positive_options = [opt for opt in positive_options if opt not in intersection]
    
        # Clean the options as strings for display
        negative_str = self.__clean_list_to_str(negative_options)
        positive_str = self.__clean_list_to_str(positive_options)
        exit_str = self.__clean_list_to_str(exit_options)

        logger.debug(f"Confirm action with negative options: {negative_str}, positive options: {positive_str} and exit options: {exit_str}")

        # Get user input, strip whitespace and convert to lowercase
        choice = input(prompt).strip().lower()

        # Validate input
        if choice not in (negative_options + positive_options + exit_options):
            print(f"[!] Invalid input. Please choose from: {positive_str} for yes, {negative_str} for no ({exit_str}) to exit.", "red")
            input("Press Enter to continue...")
            return self.__confirm_action(negative_options, positive_options, prompt)
        
        # Exit if in exit options
        if choice in exit_options:
            self.__print("[+] Exiting menu.", "gray")
            sys.exit(0)
        
        # Return False if in negative options
        if choice in negative_options:
            return False
        return True

    def __refine_confirm_options(self, options: list, type: str = "positive"):
        # Helper function to refine confirm options
        # Remove duplicates and normalize to lowercase
        refined = list(set([opt.lower() for opt in (options or [])]))

        # Add default options if to each list to save additional args

        if type == "positive":
            # Remove any default negative options that are in positive options
            default_negative = [opt for opt in self.default_negative if opt not in (options or [])]
            
        elif type == "negative":
            # Remove any default positive options that are in negative options
            default_positive = [opt for opt in self.default_positive if opt not in (options or [])]
            
        else:
            logger.warning(f"Unknown type '{type}' in refine_confirm_options. Defaulting to positive.")
            type = "positive"

        # Type is positive
        if type == "positive":
            return options + default_positive
        # Type is negative
        return options + default_negative

    def __boxify_top_bottom(self, title: bool = False, top: bool = True):
        """
        Boxify the top or bottom of the menu.
        PARAM: title - Whether this is a title box (affects margins)
               top - Whether this is the top or bottom box
        """
        # Set the line characters
        horizontal = self.border["horizontal"]
        space = self.border["space"]

        # Set the left and right border characters based on top or bottom
        left = self.border["bottom_left"]
        right = self.border["bottom_right"]
        if top:
            left = self.border["top_left"]
            right = self.border["top_right"]
        
        # Set the colour and margin based on whether this is a title or options box
        colour = self.colours["options_border"]
        margin = f"{self.border["options_margin"] * space}"
        if title:
            colour = self.colours["title_border"]
            margin = f"{self.border["title_margin"] * space}"

        # Set the overall width minus the margins
        width = self.width - (len(margin) * 2)

        # Generate the box line
        line = f"{margin}{left}{horizontal * (width - 2)}{right}"

        # Print the line with the appropriate colour
        self.__print(line, colour=colour)

    def __boxify_middle(self, text: str, type: str = None) -> None:
        """
        Add the middle part of a whole box.
        PARAM: text - The text to boxify
               type - The type of box (title, title_info, title_border, option)
        """

        # Requires a type, return if nto
        if not type:
            logger.error("Type is required for boxify_middle.")
            return
        
        # Clean the type
        type = type.lower().strip()

        # Set the border characters
        space = self.border["space"]
        vertical = self.border["vertical"]

        # Set defaults
        margin = self.border["options_margin"]
        colour = self.colours["options_border"]
        text_colour = self.colours["option"]
        center = False
        
        # Setup is:
        # |---margin---|--border--|--space--|-------text-------|--space--|--border--|---margin---|
        # Though the final margin is not printed, just spaces process it anyway for consistency


        # Set title generics
        if "title" in type:

            # Set the border specifics
            margin = self.border["title_margin"]
            colour = self.border["title_colour"]
            space = self.border["title_space"]
            center = True

            # Apply the text colours based on type - no text in title_space
            text_colour = self.colours["title"]
            if type == "title_info":
                text_colour = self.colours["title_info"]
        
        # Build the full line - starting with the margin
        margin_space = f"{" "*margin}"

        # Add the borders
        line_left = f"{margin_space}{vertical}{space*3}"
        line_left = Colours.colour_text(line_left, colour=colour)
        line_right = f"{space*3}{vertical}{margin_space}"
        line_right = Colours.colour_text(line_right, colour=colour)

        # Calculate the available width for text - account for ansi codes in borders
        left_width = len(self.__strip_ansi_codes(line_left))
        right_width = len(self.__strip_ansi_codes(line_right))
        available_width = self.width - left_width - right_width

        # Truncate the text if it's too long
        if len(text) > available_width:
            text= text[:available_width - 3] + "..."
        
        # Set the colour of the text
        text = Colours.colour_text(text, colour=text_colour, bold=True)
        text_width = len(self.__strip_ansi_codes(text))
        
        # Readjust for more ansi code just added
        available_width -= text_width - len(text)

        # Set the line out by default
        line = text.ljust(available_width)

        # Center the text if flagged
        if center:
            line = text.center(available_width,space)
            
        # Combine the full line
        full_line = f"{line_left}{line}{line_right}"

        # Print the line with the appropriate colour
        self.__print(full_line, colour=colour)

    def exit_menu(self):
        # Exit the menu
        self.__print("[+] Exiting menu.", "gray")
        sys.exit(0)

    def return_to_previous_menu(self):
        # Return to the previous menu if it exists
        if self.previous_menu:
            self.__print("[+] Returning to previous menu.", "gray")
            self.previous_menu.launch()
        else:
            self.__print("[!] No previous menu to return to.", "red")
            input("Press Enter to continue...")
    
    def __clear(self):
        # Clear the terminal screen
        os.system('clear' if os.name == 'posix' else 'cls')

    def __generate_header(self):
        # Generate a consistent header for all menus
        timestamp = datetime.datetime.now().isoformat(timespec="seconds")
        node = os.getenv("NODE_NAME", "LUXFORGE")
        
        # Print the top border
        self.__boxify_top_bottom(title=True, top=True)
        
        # Print the title and timestamp
        self.__boxify_middle(text="", type="title_space") # Blank line after top border
        self.__boxify_middle(text=self.menu_name, type="title")
        self.__boxify_middle(text=f"{node}  ::  {timestamp}", type="title_info")
        self.__boxify_middle(text="", type="title_space") # Blank line before bottom border
        self.__boxify_top_bottom(title=True, top=False)

        # Print the options header
        self.__boxify_top_bottom(title=False, top=True)
        self.__boxify_middle(text="", type="options_space") # Blank line after top border
    
    def __clean_list_to_str(self, items: list):
        # Helper function to clean a list of items to a string for display
        # Casts the NoneType to a string 'None' to avoid issues
        cleaned = [str(item) if item is not None else "'None'" for item in items]
        return ", ".join(cleaned)

    def __strip_ansi_codes(self, text: str) -> str:
        # Helper function to strip ANSI colour codes from a string
        import re
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', text)
    
    def __interactive_select(self, options: dict) -> str:
        """
        Interactive selection of options using arrow keys and typing.
        PARAM: options - Dictionary of options to display
        RETURNS: Selected option key as string
        """

        # Get the keys as a list for indexing
        keys = list(options.keys())
        selected = 0

        # Wait for user input
        while True:
            self.__clear()
            self.__generate_header()

            # Render options
            for i, key in enumerate(keys):
                desc, _ = options[key]
                prefix = "➤  " if i == selected else "    "
                colour = self.border["option_colour"]

                # Highlight the selected option
                if i == selected:
                    colour = "cyan"
                styled = Colours.colour_text(f"{prefix} {key} | {desc}", colour=colour)
                if key in self.back_options:
                    self.__boxify_middle(text="", type="options_space") # Add a blank line before back options
                elif key in self.exit_options:
                    self.__boxify_middle(text="", type="options_space") # Add a blank line before exit options

                self.__boxify_middle(text=styled, type="option")

            self.__boxify_middle(text="", type="options_space") # Add a blank line after options
            self.__boxify_middle(text=f"[?] Select an option ({self.valid_options_as_str}): ", type="option")
        

                
            # Show typed input
            typed = self.key_handler.get_typed()
            
            self.__boxify_top_bottom(title=False, top=False)

            # Handle key
            raw = self.key_handler.get_key()
            action = self.key_handler.interpret(raw)

            if action == 'UP':
                selected = (selected - 1) % len(keys)
            elif action == 'DOWN':
                selected = (selected + 1) % len(keys)
            elif action == 'ENTER':
                if typed and typed in keys:
                    self.key_handler.reset()
                    return typed
                else:
                    self.key_handler.reset()
                    return keys[selected]
            elif action == 'BACKSPACE':
                # See if we have a previous menu, if so then return to it
                if self.previous_menu:
                    self.previous_menu.launch()
                else:
                    self.key_handler.reset()
                    return None
            elif action == 'ESC':
                self.key_handler.reset()
                return None

            # Handle alphabetic input for quick selection
            # Validate the input
            else: 
                if self.__validate_user_input(action):
                    self.__handle_option(action)
                else:
                    logger.error(f"Should not get to this point, break in logic!! Action: {action}")
        



# Menu if launched directly - used for testing
if __name__ == "__main__":
    menu = Menu()
    menu.launch()