"""Graphical keyboard widget for trigger key selection."""

import tkinter as tk
from tkinter import messagebox
from key_defs import KEYBOARD_LAYOUT


class KeyboardSelector(tk.Frame):
    """Visual keyboard layout for clicking to select a trigger key.

    Displays keys in CardPuter physical layout. Unselectable keys
    (Fn, ;, comma, period, slash) are grayed out.
    Keys that already have macros assigned are shown in lighter blue
    and cannot be selected (must delete the existing macro first).

    Callback: on_select(trigger_key_name) is called when a selectable
    key is clicked.
    """

    # Layout constants
    KEY_W = 46
    KEY_H = 36
    GAP = 3
    PADDING = 6

    # Colors
    COLOR_NORMAL   = "#e0e0e0"   # unassigned key
    COLOR_ASSIGNED = "#b3e0f7"   # already has a macro (lighter blue)
    COLOR_HOVER    = "#c8e6f8"   # mouse hover on selectable key
    COLOR_SELECTED = "#4fc3f7"   # currently selected (deep blue)
    COLOR_DISABLED = "#a0a0a0"   # not selectable (Fn, ; etc.)
    COLOR_TEXT     = "#000000"
    COLOR_DIS_TEXT = "#666666"

    def __init__(self, master, on_select=None, **kwargs):
        super().__init__(master, **kwargs)
        self.on_select = on_select
        self._selected = None
        self._buttons = {}
        self._assigned = set()

        max_cols = max(len(row) for row in KEYBOARD_LAYOUT)
        canvas_w = max_cols * (self.KEY_W + self.GAP) - self.GAP + self.PADDING * 2
        canvas_h = len(KEYBOARD_LAYOUT) * (self.KEY_H + self.GAP) - self.GAP + self.PADDING * 2

        self.canvas = tk.Canvas(self, width=canvas_w, height=canvas_h,
                                bg="#ffffff", highlightthickness=0)
        self.canvas.pack()

        self._build_keys()

    def _build_keys(self):
        y = self.PADDING
        for row in KEYBOARD_LAYOUT:
            x = self.PADDING
            for label, trigger_name in row:
                selectable = trigger_name is not None

                if selectable:
                    bg = self.COLOR_NORMAL
                    fg = self.COLOR_TEXT
                    cursor = "hand2"
                else:
                    bg = self.COLOR_DISABLED
                    fg = self.COLOR_DIS_TEXT
                    cursor = ""

                btn = tk.Label(
                    self.canvas, text=label,
                    bg=bg, fg=fg,
                    font=("Consolas", 9, "bold"),
                    relief=tk.RAISED, borderwidth=1,
                    cursor=cursor,
                )
                btn.place(x=x, y=y, width=self.KEY_W, height=self.KEY_H)

                if selectable:
                    btn.bind("<Button-1>",
                             lambda e, tn=trigger_name: self._on_click(tn))
                    btn.bind("<Enter>",
                             lambda e, tn=trigger_name: self._on_enter(tn))
                    btn.bind("<Leave>",
                             lambda e, tn=trigger_name: self._on_leave(tn))
                    self._buttons[trigger_name] = btn

                x += self.KEY_W + self.GAP
            y += self.KEY_H + self.GAP

    def _base_color(self, trigger_name):
        """Return the resting color for a key."""
        if trigger_name == self._selected:
            return self.COLOR_SELECTED
        if trigger_name in self._assigned:
            return self.COLOR_ASSIGNED
        return self.COLOR_NORMAL

    def _on_click(self, trigger_name):
        # Block selection of already-assigned keys
        if trigger_name in self._assigned and trigger_name != self._selected:
            messagebox.showwarning(
                "Trigger Key Occupied",
                f"'{trigger_name}' is already used as a trigger key.\n\n"
                "Please delete the existing macro first,\n"
                "or choose another key.")
            return

        # Deselect previous
        if self._selected and self._selected in self._buttons:
            prev = self._selected
            self._selected = None
            self._buttons[prev].config(
                bg=self._base_color(prev),
                cursor="hand2" if prev not in self._assigned else "")

        # Select new
        self._selected = trigger_name
        self._buttons[trigger_name].config(bg=self.COLOR_SELECTED)
        if self.on_select:
            self.on_select(trigger_name)

    def _on_enter(self, trigger_name):
        if trigger_name == self._selected:
            return
        # Assigned keys don't get hover effect
        if trigger_name in self._assigned:
            return
        self._buttons[trigger_name].config(bg=self.COLOR_HOVER)

    def _on_leave(self, trigger_name):
        if trigger_name == self._selected:
            return
        self._buttons[trigger_name].config(
            bg=self._base_color(trigger_name))

    def set_selected(self, trigger_name):
        """Programmatically select a key."""
        # Deselect old
        if self._selected and self._selected in self._buttons:
            prev = self._selected
            self._selected = None
            self._buttons[prev].config(
                bg=self._base_color(prev),
                cursor="hand2" if prev not in self._assigned else "")
        # Select new
        self._selected = trigger_name
        if trigger_name and trigger_name in self._buttons:
            self._buttons[trigger_name].config(
                bg=self.COLOR_SELECTED, cursor="hand2")

    def get_selected(self):
        return self._selected

    def set_assigned_keys(self, keys):
        """Update which keys have macros assigned (shown in lighter blue).

        Args:
            keys: set or list of trigger_key_name strings
        """
        self._assigned = set(keys)
        for tn, btn in self._buttons.items():
            if tn != self._selected:
                is_assigned = tn in self._assigned
                btn.config(
                    bg=self.COLOR_ASSIGNED if is_assigned else self.COLOR_NORMAL,
                    cursor="" if is_assigned else "hand2")
