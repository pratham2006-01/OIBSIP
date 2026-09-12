"""
Cipher — Password Generator Backend
====================================
Flask API that reuses the exact generation logic from the original
tkinter app (secrets-based, cryptographically secure). The frontend
(templates/index.html) calls POST /api/generate and renders the result.

The password is generated here, returned once in the response, and
never written to disk or logged — same guarantee as the desktop version.
"""

import secrets
import string

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# Characters that are easy to visually confuse with each other.
AMBIGUOUS_CHARS = "0O1lI|`'\""


# ----------------------------------------------------------------------
# CORE GENERATION LOGIC (ported directly from PasswordGeneratorApp)
# ----------------------------------------------------------------------
def clean(charset, exclude_ambiguous):
    """Remove ambiguous characters from a set, if requested."""
    if exclude_ambiguous:
        return "".join(ch for ch in charset if ch not in AMBIGUOUS_CHARS)
    return charset


def get_selected_char_sets(upper, lower, digits, symbols, exclude_ambiguous):
    """Build the list of character sets the user selected."""
    selected = []
    if upper:
        selected.append(clean(string.ascii_uppercase, exclude_ambiguous))
    if lower:
        selected.append(clean(string.ascii_lowercase, exclude_ambiguous))
    if digits:
        selected.append(clean(string.digits, exclude_ambiguous))
    if symbols:
        selected.append(clean(string.punctuation, exclude_ambiguous))
    return selected


def generate_password(length, selected_sets):
    """
    Generates a cryptographically secure password using secrets,
    guaranteeing at least one character from each selected set.
    """
    # Step 1: guarantee one character from EACH selected type
    password_chars = [secrets.choice(charset) for charset in selected_sets]

    # Step 2: combined pool for the remaining characters
    combined_pool = "".join(selected_sets)

    # Step 3: fill remaining length
    remaining = length - len(password_chars)
    password_chars += [secrets.choice(combined_pool) for _ in range(remaining)]

    # Step 4: secure Fisher-Yates shuffle
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

    return "".join(password_chars)


def score_password(password):
    """
    Returns (label, fill_ratio) based purely on password length.
    Four tiers: weak, medium, strong, titanic.
    """
    length = len(password)

    if length < 12:
        return "weak", 0.25
    elif length < 20:
        return "medium", 0.5
    elif length < 32:
        return "strong", 0.75
    else:
        return "titanic", 1.0


# ----------------------------------------------------------------------
# ROUTES
# ----------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(silent=True) or {}

    try:
        length = int(data.get("length", 12))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid length"}), 400

    upper = bool(data.get("upper", True))
    lower = bool(data.get("lower", True))
    digits = bool(data.get("digits", True))
    symbols = bool(data.get("symbols", False))
    exclude_ambiguous = bool(data.get("excludeAmbiguous", False))

    if length < 8 or length > 64:
        return jsonify({"error": "length must be between 8 and 64"}), 400

    selected_sets = get_selected_char_sets(upper, lower, digits, symbols, exclude_ambiguous)

    if len(selected_sets) < 2:
        return jsonify({"error": "select at least 2 character types"}), 400

    if any(len(charset) == 0 for charset in selected_sets):
        return jsonify({"error": "a selected type is empty after exclusions"}), 400

    password = generate_password(length, selected_sets)
    label, ratio = score_password(password)

    return jsonify({
        "password": password,
        "strength": {"label": label, "ratio": ratio}
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)