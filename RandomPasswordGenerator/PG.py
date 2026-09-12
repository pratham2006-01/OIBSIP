"""
Random Password Generator - BEGINNER (Command-Line) Version
==============================================================

Features:
- Prompts for password length (minimum 8 characters enforced)
- Prompts for which character types to include
  (uppercase, lowercase, numbers, symbols) - at least 2 must be chosen
- Generates a password that satisfies all chosen criteria
- Validates all user input and re-prompts on bad input
- Lets the user generate more passwords in a loop without restarting

Tech: random, string  (standard library only)
"""

import random   # used to randomly choose characters for the password
import string   # gives us ready-made character sets (letters, digits, punctuation)


def get_password_length():
    """
    Ask the user for a password length.
    Keeps asking until they give a valid integer >= 8.
    """
    while True:
        raw_value = input("Enter desired password length (minimum 8): ").strip()

        # Make sure what they typed is actually a number
        if not raw_value.isdigit():
            print("  -> Please enter a whole number.\n")
            continue

        length = int(raw_value)

        # Enforce the minimum length rule
        if length < 8:
            print("  -> Password length must be at least 8 characters.\n")
            continue

        return length  # valid length found, exit the loop


def get_character_types():
    """
    Ask the user which character categories to include.
    Requires at least 2 categories to be selected before continuing.
    Returns a dictionary of True/False flags for each category.
    """
    while True:
        print("\nWhich character types do you want to include?")
        print("(Answer y/n for each. You must choose at least 2 types.)")

        use_upper = input("  Include UPPERCASE letters (A-Z)? (y/n): ").strip().lower() == "y"
        use_lower = input("  Include lowercase letters (a-z)? (y/n): ").strip().lower() == "y"
        use_digits = input("  Include numbers (0-9)? (y/n): ").strip().lower() == "y"
        use_symbols = input("  Include symbols (!@#$...)? (y/n): ").strip().lower() == "y"

        selected_count = sum([use_upper, use_lower, use_digits, use_symbols])

        if selected_count < 2:
            print("  -> You must select at least 2 character types. Try again.\n")
            continue

        return {
            "upper": use_upper,
            "lower": use_lower,
            "digits": use_digits,
            "symbols": use_symbols,
        }


def build_character_pool(types_selected):
    """
    Given the dictionary of selected types, build:
      1. The full pool of allowed characters (for random filling)
      2. A list of "guaranteed" character sets, one per selected type,
         so we can later ensure the password contains at least one
         character from EVERY selected type.
    """
    pool = ""              # combined pool of every allowed character
    guaranteed_sets = []   # one string per selected category

    if types_selected["upper"]:
        pool += string.ascii_uppercase
        guaranteed_sets.append(string.ascii_uppercase)

    if types_selected["lower"]:
        pool += string.ascii_lowercase
        guaranteed_sets.append(string.ascii_lowercase)

    if types_selected["digits"]:
        pool += string.digits
        guaranteed_sets.append(string.digits)

    if types_selected["symbols"]:
        pool += string.punctuation
        guaranteed_sets.append(string.punctuation)

    return pool, guaranteed_sets


def generate_password(length, pool, guaranteed_sets):
    """
    Generate a random password of the given length using characters
    from 'pool', while guaranteeing at least one character from each
    set in 'guaranteed_sets'.
    """
    # Step 1: pick one guaranteed character from each selected type
    password_chars = [random.choice(char_set) for char_set in guaranteed_sets]

    # Step 2: fill the rest of the password length with random choices
    # from the full combined pool
    remaining_length = length - len(password_chars)
    password_chars += [random.choice(pool) for _ in range(remaining_length)]

    # Step 3: shuffle so the guaranteed characters aren't always at the front
    random.shuffle(password_chars)

    # Step 4: join the list of characters into a single string
    return "".join(password_chars)


def main():
    """Main program loop: generate passwords until the user quits."""
    print("=" * 50)
    print("       RANDOM PASSWORD GENERATOR (Beginner CLI)")
    print("=" * 50)

    while True:
        # 1. Get validated length from the user
        length = get_password_length()

        # 2. Get validated character type selections from the user
        types_selected = get_character_types()

        # 3. Build the character pool + guaranteed sets based on selections
        pool, guaranteed_sets = build_character_pool(types_selected)

        # 4. Generate the password
        password = generate_password(length, pool, guaranteed_sets)

        # 5. Display the result
        print("\nYour generated password is:")
        print(f"  {password}\n")

        # 6. Ask if the user wants another password (without restarting the script)
        again = input("Generate another password? (y/n): ").strip().lower()
        if again != "y":
            print("\nGoodbye! Stay secure. 🔒")
            break
        print()  # blank line for spacing before the next round


# Standard Python entry point check:
# This ensures main() only runs when this file is executed directly,
# not when it's imported as a module elsewhere.
if __name__ == "__main__":
    main()