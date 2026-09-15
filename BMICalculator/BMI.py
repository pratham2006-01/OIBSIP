
def get_positive_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("  -> That's not a number. Please enter something like 70 or 1.75.")
            continue

        if value <= 0:
            print("  -> Value has to be greater than zero. Try again.")
            continue

        return value


def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


def main():
    print("=== BMI Calculator ===")
    print("Enter your details below (weight in kg, height in meters).\n")

    weight = get_positive_float("Weight (kg): ")
    height = get_positive_float("Height (m): ")

    bmi = weight / (height ** 2)
    category = classify_bmi(bmi)

    print("\n--- Result ---")
    print(f"Your BMI is: {bmi:.2f}")
    print(f"Category: {category}")

    
    if height > 3:
        print("\nNote: that height seems really tall - did you mean to enter it in meters?")


if __name__ == "__main__":
    while True:
        main()
        again = input("\nRun again? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            break
        print()