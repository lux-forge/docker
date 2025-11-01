#!/usr/bin/env python3

# passwordEngine.py
# Author: Luxforge
# Password generation utility for user management.

import random
import string
import math


class PasswordEngine:
    """
    Password authentication engine for generating and validating passwords.
    """
    PASSWORD_COMPLEXITY = {
        "min_length": 12,
        "max_length": 20,
        "lower": True,
        "caps": True,
        "digits": True,
        "special": True,
        "minimum_entropy": 50.0  # in bits
    }

    def __init__(self, complexity: dict = PASSWORD_COMPLEXITY):
        self.PASSWORD_COMPLEXITY = complexity

    @staticmethod
    def generate_password(attempts=5) -> str:
        """
        Generate a random password based on the defined complexity rules.
        Will include at least one character from each enabled category.
        Ensures the upper scale of max length is used.
        RETURNS: str - The generated password.
        """

        if attempts <= 0:
            raise ValueError("Maximum attempts reached for password generation.")
        
        complexity = PasswordEngine.PASSWORD_COMPLEXITY

        # Determine length - use max length for stronger passwords
        length = complexity.get("max_length", 64)

        pools = {
            "lower": string.ascii_lowercase if complexity.get("lower", True) else "",
            "caps": string.ascii_uppercase if complexity.get("caps", False) else "",
            "digits": string.digits if complexity.get("digits", False) else "",
            "special": string.punctuation if complexity.get("special", False) else ""
        }

        # Filter out empty pools
        active_pools = {k: v for k, v in pools.items() if v}
        
        # Ensure at least one character from each active pool
        if not active_pools:
            raise ValueError("No character pools enabled.")

        # Build the password - ensure each category is represented at least once
        required = [random.choice(pool) for pool in active_pools.values()]

        # Fill the remaining length with random choices from the combined pool
        remaining = length - len(required)

        # Create a combined pool
        combined_pool = "".join(active_pools.values())

        # Fill the remaining length with random choices from the combined pool
        filler = random.choices(combined_pool, k=remaining)

        # Combine required and filler characters
        password = required + filler

        # Shuffle the result to avoid predictable patterns
        random.shuffle(password)

        # Ensure it is valid, else regenerate
        if not PasswordEngine.validate_password("".join(password)):
            return PasswordEngine.generate_password(attempts - 1)

        return "".join(password)

    @staticmethod
    def validate_password(password: str, complexity: dict = None) -> bool:
        """
        Validate a password against the defined complexity rules.
        PARAMS: password: str - The password to validate.
        RETURNS: bool - True if valid, False otherwise.
        """
        
        # Validate based on complexity rules
        if complexity is None:
            complexity = PasswordEngine.PASSWORD_COMPLEXITY
        
        if not password:
            print("Password is empty.")
            return False
        
        # Retrieve password length
        length = len(password)
        password_passes = True

        # Check length constraints - concat conditions so all are checked before returning
        if length < complexity.get("min_length", PasswordEngine.PASSWORD_COMPLEXITY["min_length"]):
            print("Password does not meet minimum length requirements.")
            password_passes = False

        if length > complexity.get("max_length", PasswordEngine.PASSWORD_COMPLEXITY["max_length"]):
            print("Password exceeds maximum length requirements.")
            password_passes = False

        if complexity.get("lower", PasswordEngine.PASSWORD_COMPLEXITY["lower"]) and not any(c in string.ascii_lowercase for c in password):
            print("Password must contain at least one lowercase letter.")
            password_passes = False

        if complexity.get("caps", PasswordEngine.PASSWORD_COMPLEXITY["caps"]) and not any(c in string.ascii_uppercase for c in password):
            print("Password must contain at least one uppercase letter.")
            password_passes = False

        if complexity.get("digits", PasswordEngine.PASSWORD_COMPLEXITY["digits"]) and not any(c in string.digits for c in password):
            print("Password must contain at least one digit.")
            password_passes = False

        if complexity.get("special", PasswordEngine.PASSWORD_COMPLEXITY["special"]) and not any(c in string.punctuation for c in password):
            print("Password must contain at least one special character.")
            password_passes = False

        if PasswordEngine.estimate_entropy(password) < 100:
            print(f"Password entropy too low ({PasswordEngine.estimate_entropy(password)}) -- try a more complex password.")
            password_passes = False

        return password_passes

    @staticmethod
    def estimate_entropy(password: str, complexity: dict = None) -> float:
        """
        Estimate Shannon entropy of a password based on character pool size and length.
        RETURNS: float - Estimated entropy in bits.
        """
        if not password:
            return 0.0

        if not complexity:
            complexity = PasswordEngine.PASSWORD_COMPLEXITY

        pool_size = 0
        if complexity.get("lower", True):
            pool_size += len(string.ascii_lowercase)
        if complexity.get("caps", False):
            pool_size += len(string.ascii_uppercase)
        if complexity.get("digits", False):
            pool_size += len(string.digits)
        if complexity.get("special", False):
            pool_size += len(string.punctuation)

        if pool_size == 0:
            raise ValueError("No character pools enabled.")

        entropy = len(password) * math.log2(pool_size)
        return round(entropy, 2)

    
if __name__ == "__main__":
    engine = PasswordEngine()
    pwd = engine.generate_password()
    print(f"Generated Password: {pwd}")
    print(f"Is Valid: {engine.validate_password(pwd)}")
    print(f"Estimated Entropy: {engine.estimate_entropy(pwd)} bits")