"""
Random Password Generator - ADVANCED (GUI) Version
==============================================================

Features:
- GUI built with tkinter (spinbox for length, checkboxes for character types)
- Uses the 'secrets' module (cryptographically secure) instead of 'random'
- Password strength indicator (Weak / Medium / Strong) with a colored bar
- Guarantees at least one character from every SELECTED type
- "Copy to Clipboard" button (uses pyperclip) - also auto-copies on generation
- Checkbox to exclude ambiguous characters (0, O, l, 1, I, etc.)
- Session-only history of the last 5 generated passwords (never written to disk)

Tech: secrets, string, tkinter, pyperclip
"""

import secrets   # cryptographically secure random choices (safe for passwords)
import string    # ready-made character sets (letters, digits, punctuation)
import tkinter as tk
from tkinter import ttk, messagebox

# pyperclip handles clipboard copy/paste. If it isn't installed, we fall back
# gracefully so the rest of the app still works (just without auto-copy).
try:
    import pyperclip
    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


# Characters that are easy to visually confuse with each other.
# If the user checks "exclude ambiguous characters", these get stripped
# from every character set before generation.
AMBIGUOUS_CHARS = "0O1lI|`'\""


class PasswordGeneratorApp:
    """Main application class - holds all GUI widgets and generation logic."""

    def __init__(self, root):
        self.root = root
        self.root.title("Secure Password Generator")
        self.root.geometry("480x620")
        self.root.resizable(False, False)

        # In-memory history of generated passwords (this session only).
        # We deliberately never save this to a file, per the security requirement.
        self.history = []

        self._build_ui()

    # ------------------------------------------------------------------
    # UI CONSTRUCTION
    # ------------------------------------------------------------------
    def _build_ui(self):
        """Builds and lays out every widget in the window."""

        padding = {"padx": 16, "pady": 6}

        title_label = ttk.Label(
            self.root, text="🔐 Password Generator",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(16, 10))

        # ---------------- Length control (Spinbox + Slider) ----------------
        length_frame = ttk.LabelFrame(self.root, text="Password Length")
        length_frame.pack(fill="x", **padding)

        # IntVar keeps the spinbox and slider in sync automatically
        self.length_var = tk.IntVar(value=12)

        # Spinbox: lets the user type/click a specific number (min 8 enforced)
        self.length_spinbox = ttk.Spinbox(
            length_frame, from_=8, to=64, textvariable=self.length_var,
            width=6, command=self._sync_slider_from_spinbox
        )
        self.length_spinbox.grid(row=0, column=0, padx=10, pady=10)

        # Slider: visual/quick way to adjust length, also min 8
        self.length_slider = ttk.Scale(
            length_frame, from_=8, to=64, orient="horizontal",
            command=self._sync_spinbox_from_slider, length=300
        )
        self.length_slider.set(12)
        self.length_slider.grid(row=0, column=1, padx=10, pady=10)

        # ---------------- Character type checkboxes ----------------
        types_frame = ttk.LabelFrame(self.root, text="Character Types (choose at least 2)")
        types_frame.pack(fill="x", **padding)

        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)

        ttk.Checkbutton(types_frame, text="Uppercase (A-Z)", variable=self.use_upper,
                         command=self._update_strength_preview).grid(row=0, column=0, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(types_frame, text="Lowercase (a-z)", variable=self.use_lower,
                         command=self._update_strength_preview).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(types_frame, text="Numbers (0-9)", variable=self.use_digits,
                         command=self._update_strength_preview).grid(row=0, column=1, sticky="w", padx=10, pady=4)
        ttk.Checkbutton(types_frame, text="Symbols (!@#$...)", variable=self.use_symbols,
                         command=self._update_strength_preview).grid(row=1, column=1, sticky="w", padx=10, pady=4)

        # ---------------- Ambiguous character exclusion ----------------
        self.exclude_ambiguous = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.root, text="Exclude ambiguous characters (0, O, l, 1, I, |, etc.)",
            variable=self.exclude_ambiguous
        ).pack(anchor="w", padx=20, pady=(0, 6))

        # ---------------- Generate button ----------------
        generate_btn = ttk.Button(self.root, text="Generate Password", command=self.generate_password)
        generate_btn.pack(pady=(6, 10))

        # ---------------- Result display + copy button ----------------
        result_frame = ttk.Frame(self.root)
        result_frame.pack(fill="x", **padding)

        self.password_var = tk.StringVar(value="")
        self.password_entry = ttk.Entry(
            result_frame, textvariable=self.password_var,
            font=("Consolas", 13), justify="center", state="readonly"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=4)

        self.copy_btn = ttk.Button(result_frame, text="Copy", command=self.copy_to_clipboard)
        self.copy_btn.pack(side="left", padx=(8, 0))

        # ---------------- Strength indicator ----------------
        strength_frame = ttk.LabelFrame(self.root, text="Strength")
        strength_frame.pack(fill="x", **padding)

        self.strength_label = ttk.Label(strength_frame, text="—", font=("Segoe UI", 11, "bold"))
        self.strength_label.pack(anchor="w", padx=10, pady=(6, 2))

        # A Canvas is used as a simple colored bar (tkinter has no built-in
        # progress bar with custom colors, so we draw a rectangle manually).
        self.strength_canvas = tk.Canvas(strength_frame, height=18, width=420,
                                          bg="#e0e0e0", highlightthickness=0)
        self.strength_canvas.pack(padx=10, pady=(0, 10))

        # ---------------- History (last 5 passwords) ----------------
        history_frame = ttk.LabelFrame(self.root, text="History (this session only, last 5)")
        history_frame.pack(fill="both", expand=True, **padding)

        self.history_listbox = tk.Listbox(history_frame, font=("Consolas", 10), height=6)
        self.history_listbox.pack(fill="both", expand=True, padx=8, pady=8)

        # Status bar for small messages (e.g. "Copied!")
        self.status_var = tk.StringVar(value="Ready.")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, anchor="w",
                                foreground="gray")
        status_bar.pack(fill="x", padx=16, pady=(0, 8))

    # ------------------------------------------------------------------
    # SLIDER / SPINBOX SYNC HELPERS
    # ------------------------------------------------------------------
    def _sync_slider_from_spinbox(self):
        """Keep the slider in sync when the spinbox value changes."""
        try:
            value = int(self.length_var.get())
        except (tk.TclError, ValueError):
            value = 12
        self.length_slider.set(value)

    def _sync_spinbox_from_slider(self, value_str):
        """Keep the spinbox in sync when the slider is dragged."""
        # Sliders report float strings like "12.0" - round to a whole number
        value = round(float(value_str))
        self.length_var.set(value)

    # ------------------------------------------------------------------
    # CORE GENERATION LOGIC
    # ------------------------------------------------------------------
    def _get_selected_char_sets(self):
        """
        Build the list of character sets the user has selected, applying
        the 'exclude ambiguous characters' filter if checked.
        Returns a list of (name, character_set_string) tuples.
        """
        selected = []

        def clean(charset):
            """Remove ambiguous characters from a set, if that option is checked."""
            if self.exclude_ambiguous.get():
                return "".join(ch for ch in charset if ch not in AMBIGUOUS_CHARS)
            return charset

        if self.use_upper.get():
            selected.append(("upper", clean(string.ascii_uppercase)))
        if self.use_lower.get():
            selected.append(("lower", clean(string.ascii_lowercase)))
        if self.use_digits.get():
            selected.append(("digits", clean(string.digits)))
        if self.use_symbols.get():
            selected.append(("symbols", clean(string.punctuation)))

        return selected

    def generate_password(self):
        """
        Validates inputs, then generates a cryptographically secure
        password using the 'secrets' module, guaranteeing at least one
        character from each selected type.
        """
        length = int(self.length_var.get())

        # --- Validation: minimum length ---
        if length < 8:
            messagebox.showerror("Invalid Length", "Password length must be at least 8 characters.")
            return

        selected_sets = self._get_selected_char_sets()

        # --- Validation: at least 2 character types selected ---
        if len(selected_sets) < 2:
            messagebox.showerror(
                "Not Enough Character Types",
                "Please select at least 2 character types."
            )
            return

        # --- Validation: after excluding ambiguous chars, sets can't be empty ---
        if any(len(charset) == 0 for _, charset in selected_sets):
            messagebox.showerror(
                "Empty Character Set",
                "One of your selected character types has no characters left "
                "after excluding ambiguous characters. Try unchecking that option."
            )
            return

        # Step 1: guarantee at least one character from EACH selected type,
        # using secrets.choice() (cryptographically secure, unlike random.choice)
        password_chars = [secrets.choice(charset) for _, charset in selected_sets]

        # Step 2: build the combined pool of all allowed characters for the rest
        combined_pool = "".join(charset for _, charset in selected_sets)

        # Step 3: fill remaining length with secure random choices from the pool
        remaining = length - len(password_chars)
        password_chars += [secrets.choice(combined_pool) for _ in range(remaining)]

        # Step 4: securely shuffle the list so guaranteed chars aren't predictable
        # (Fisher-Yates shuffle using secrets.randbelow for each swap)
        for i in range(len(password_chars) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            password_chars[i], password_chars[j] = password_chars[j], password_chars[i]

        password = "".join(password_chars)

        # Display it in the read-only entry field
        self.password_var.set(password)

        # Update strength meter based on the ACTUAL generated password
        self._update_strength_display(password)

        # Add to session history (keep only the last 5)
        self._add_to_history(password)

        # Auto-copy to clipboard on generation, per the spec
        self.copy_to_clipboard(silent=True)
        self.status_var.set("Password generated and copied to clipboard.")

    # ------------------------------------------------------------------
    # STRENGTH METER
    # ------------------------------------------------------------------
    def _score_password(self, password):
        """
        Calculates a simple strength score based on length and character
        diversity. Returns (label, color, fill_ratio).
        """
        length = len(password)
        variety = sum([
            any(c.isupper() for c in password),
            any(c.islower() for c in password),
            any(c.isdigit() for c in password),
            any(c in string.punctuation for c in password),
        ])

        # Simple point system: longer passwords + more variety = stronger
        score = 0
        score += min(length, 20)      # up to 20 points for length (caps at 20 chars)
        score += variety * 10          # up to 40 points for using all 4 char types

        if score < 25:
            return "Weak", "#e74c3c", 0.33      # red
        elif score < 45:
            return "Medium", "#f39c12", 0.66    # orange
        else:
            return "Strong", "#27ae60", 1.0      # green

    def _update_strength_display(self, password):
        """Redraws the strength label + colored bar for the given password."""
        label, color, ratio = self._score_password(password)
        self.strength_label.config(text=f"Strength: {label}", foreground=color)

        self.strength_canvas.delete("all")
        bar_width = int(420 * ratio)
        self.strength_canvas.create_rectangle(0, 0, bar_width, 18, fill=color, outline="")

    def _update_strength_preview(self):
        """
        Called when checkboxes change (before generating). Just resets the
        display since we don't have an actual password to score yet.
        """
        self.strength_label.config(text="—", foreground="black")
        self.strength_canvas.delete("all")

    # ------------------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------------------
    def _add_to_history(self, password):
        """Adds a password to the in-memory history list, capped at 5 entries."""
        self.history.insert(0, password)   # newest first
        self.history = self.history[:5]    # keep only the last 5

        # Refresh the listbox widget
        self.history_listbox.delete(0, tk.END)
        for idx, pwd in enumerate(self.history, start=1):
            self.history_listbox.insert(tk.END, f"{idx}. {pwd}")

    # ------------------------------------------------------------------
    # CLIPBOARD
    # ------------------------------------------------------------------
    def copy_to_clipboard(self, silent=False):
        """Copies the currently displayed password to the system clipboard."""
        password = self.password_var.get()

        if not password:
            if not silent:
                messagebox.showinfo("Nothing to Copy", "Generate a password first.")
            return

        if CLIPBOARD_AVAILABLE:
            pyperclip.copy(password)
            if not silent:
                self.status_var.set("Copied to clipboard!")
        else:
            # pyperclip missing - fall back to tkinter's own clipboard so
            # copy still works even without the extra dependency installed.
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            if not silent:
                self.status_var.set("Copied (fallback clipboard - install pyperclip for best results).")


def main():
    """Entry point: creates the tkinter root window and runs the app."""
    root = tk.Tk()

    # Use a slightly nicer built-in theme if available
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass  # fall back to default theme if 'clam' isn't available

    app = PasswordGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()