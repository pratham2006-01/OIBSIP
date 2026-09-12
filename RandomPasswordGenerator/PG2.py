import random
import string
import math

# quick and dirty password generator, nothing fancy


def get_password_length():
    while True:
        raw = input("Enter desired password length (minimum 8): ").strip()

        if not raw.isdigit():
            print("  -> Please enter a whole number.\n")
            continue

        length = int(raw)
        if length < 8:
            print("Password length must be at least 8 characters.\n")
            continue

        return length


def get_character_types():
    while True:
        print("\nWhich character types do you want to include")
        print("Answer y/n for each. You must choose at least 2 types")

        use_upper = input("Include UPPERCASE letters(A-Z) (y/n): ").strip().lower() == "y"
        use_lower = input("Include lowercase letters(a-z) (y/n): ").strip().lower() == "y"
        use_digits = input("Include numbers(0-9) (y/n): ").strip().lower() == "y"
        use_symbols = input("Include symbols(!@#$...) (y/n): ").strip().lower() == "y"

        if sum([use_upper, use_lower, use_digits, use_symbols]) < 2:
            print("You must select at least 2 character types. Try again.\n")
            continue

        return {
            "upper": use_upper,
            "lower": use_lower,
            "digits": use_digits,
            "symbols": use_symbols,
        }


def build_character_pool(types_selected):
    # pool = everything allowed, guaranteed_sets = one entry per type
    # so we can force at least one char from each chosen type later
    pool = ""
    guaranteed_sets = []

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
    # one guaranteed char per type first
    password_chars = [random.choice(s) for s in guaranteed_sets]

    # then just fill up the rest randomly
    remaining = length - len(password_chars)
    for _ in range(remaining):
        password_chars.append(random.choice(pool))

    random.shuffle(password_chars)  # don't want the guaranteed ones stuck at the front
    return "".join(password_chars)


def main():
    print("=" * 50)
    print("      RANDOM PASSWORD GENERATOR (Beginner CLI)")
    print("=" * 50)

    while True:
        length = get_password_length()
        types_selected = get_character_types()
        pool, guaranteed_sets = build_character_pool(types_selected)
        password = generate_password(length, pool, guaranteed_sets)

        print("\nYour generated password is:")
        print(f"  {password}\n")

        again = input("Generate another password (y/n): ").strip().lower()
        if again != "y":
            print("\nStay secure")
            break
        print()


if __name__ == "__main__":
    main()