"""Main ComboKey Editor application."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
import os
import threading
import time

from key_defs import KEY_DEFS, TRIGGER_KEYS, KEYBOARD_LAYOUT, PYNPUT_KEY_MAP, HAS_PYNPUT
from models import MacroAction, Macro
from keyboard_widget import KeyboardSelector


class ComboKeyEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("CardPuter ComboKey XML Editor")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Data
        self.macros = []
        self.current_macro = -1
        self.current_file = None
        self._recording = False
        self._recorded_events = []
        self._rec_start_time = 0

        self._setup_style()
        self._build_ui()
        self._new_document()

    # --------------------------------------------------
    # Style
    # --------------------------------------------------
    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabelframe", background="#ffffff", foreground="#000000")
        style.configure("TLabelframe.Label", background="#ffffff", foreground="#007acc")
        style.configure("TLabel", background="#ffffff", foreground="#000000")
        style.configure("TButton", background="#e0e0e0", foreground="#000000", padding=4)
        style.map("TButton", background=[("active", "#d0d0d0")])
        style.configure("TEntry", fieldbackground="#f5f5f5", foreground="#000000")
        style.configure("TCombobox", fieldbackground="#f5f5f5", foreground="#000000")
        style.configure("Treeview", background="#f5f5f5", foreground="#000000",
                        fieldbackground="#f5f5f5", bordercolor="#c0c0c0",
                        rowheight=22)
        style.map("Treeview", background=[("selected", "#007acc")])
        style.configure("Treeview.Heading", background="#e0e0e0", foreground="#000000")
        style.configure("TListbox", background="#f5f5f5", foreground="#000000")
        style.configure("Small.TButton", padding=2, font=("Consolas", 8))
        style.configure("Rec.TButton", background="#d32f2f", foreground="#ffffff")
        style.map("Rec.TButton", background=[("active", "#f44336")])

    # --------------------------------------------------
    # Build UI
    # --------------------------------------------------
    def _build_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root, bg="#f0f0f0", fg="#000000")
        file_menu = tk.Menu(menubar, tearoff=0, bg="#f0f0f0", fg="#000000")
        file_menu.add_command(label="New", command=self._new_document, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self._load_xml, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self._save_xml, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_xml_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export Image...", command=self._export_image)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Main layout: Left panel + Right panel
        main_pw = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#ffffff",
                                 sashwidth=4, sashrelief=tk.RAISED)
        main_pw.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # === LEFT PANEL: Macro List ===
        left_frame = ttk.Frame(main_pw, width=200)
        main_pw.add(left_frame, minsize=180)

        list_lf = ttk.Labelframe(left_frame, text="Macros", padding=4)
        list_lf.pack(fill=tk.BOTH, expand=True)

        list_inner = ttk.Frame(list_lf)
        list_inner.pack(fill=tk.BOTH, expand=True)
        self.macro_listbox = tk.Listbox(list_inner, bg="#f5f5f5", fg="#000000",
                                        selectbackground="#007acc", font=("Consolas", 10),
                                        exportselection=False)
        scrollbar = ttk.Scrollbar(list_inner, orient=tk.VERTICAL,
                                  command=self.macro_listbox.yview)
        self.macro_listbox.config(yscrollcommand=scrollbar.set)
        self.macro_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.macro_listbox.bind("<<ListboxSelect>>", self._on_macro_select)

        # List buttons row 1: add / delete / duplicate
        list_btn_frame = ttk.Frame(list_lf)
        list_btn_frame.pack(fill=tk.X, pady=2)
        ttk.Button(list_btn_frame, text="+ New", command=self._new_macro).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_btn_frame, text="- Del", command=self._delete_macro).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_btn_frame, text="Dup", command=self._duplicate_macro).pack(side=tk.LEFT, padx=2)

        # List buttons row 2: move up / move down
        list_sort_frame = ttk.Frame(list_lf)
        list_sort_frame.pack(fill=tk.X, pady=2)
        ttk.Button(list_sort_frame, text="Up", command=self._move_macro_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_sort_frame, text="Down", command=self._move_macro_down).pack(side=tk.LEFT, padx=2)

        # === RIGHT PANEL: Editor ===
        right_frame = ttk.Frame(main_pw)
        main_pw.add(right_frame, minsize=700)

        # -- Macro settings --
        settings_lf = ttk.Labelframe(right_frame, text="Macro Settings", padding=4)
        settings_lf.pack(fill=tk.X, pady=(0, 4))

        # Settings row: Name + Consumer + Action count
        sframe = ttk.Frame(settings_lf)
        sframe.pack(fill=tk.X)

        ttk.Label(sframe, text="Trigger:").pack(side=tk.LEFT, padx=(0, 4))
        self.trigger_display = ttk.Label(sframe, text="(click keyboard below)",
                                         foreground="#888888", font=("Consolas", 10, "bold"))
        self.trigger_display.pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(sframe, text="Name:").pack(side=tk.LEFT, padx=(0, 4))
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(sframe, textvariable=self.name_var, width=22)
        self.name_entry.pack(side=tk.LEFT, padx=(0, 12))
        self.name_entry.bind("<KeyRelease>", self._on_setting_change)

        self.consumer_var = tk.BooleanVar()
        ttk.Checkbutton(sframe, text="Consumer (media)", variable=self.consumer_var,
                        command=self._on_setting_change).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(sframe, text="Repeat:").pack(side=tk.LEFT, padx=(0, 4))
        self.repeat_var = tk.StringVar(value="none")
        repeat_combo = ttk.Combobox(sframe, textvariable=self.repeat_var,
                                    values=["none", "hold"], width=6, state="readonly")
        repeat_combo.pack(side=tk.LEFT, padx=(0, 12))
        repeat_combo.bind("<<ComboboxSelected>>", self._on_setting_change)

        ttk.Label(sframe, text="Actions:").pack(side=tk.RIGHT)
        self.action_count_label = ttk.Label(sframe, text="0", foreground="#00bcd4")
        self.action_count_label.pack(side=tk.RIGHT, padx=(2, 0))

        # Keyboard selector widget
        kb_frame = ttk.Frame(settings_lf)
        kb_frame.pack(fill=tk.X, pady=(4, 0))
        self.kb_selector = KeyboardSelector(kb_frame, on_select=self._on_trigger_select)
        self.kb_selector.pack()

        # -- Action list (Treeview) --
        act_lf = ttk.Labelframe(right_frame, text="Action Sequence", padding=4)
        act_lf.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        act_inner = ttk.Frame(act_lf)
        act_inner.pack(fill=tk.BOTH, expand=True)

        columns = ("#", "Key", "Group", "Type", "Delay(ms)")
        self.action_tree = ttk.Treeview(act_inner, columns=columns, show="headings",
                                        height=12, selectmode="extended")
        self.action_tree.column("#", width=35, anchor=tk.CENTER)
        self.action_tree.column("Key", width=120, anchor=tk.CENTER)
        self.action_tree.column("Group", width=50, anchor=tk.CENTER)
        self.action_tree.column("Type", width=60, anchor=tk.CENTER)
        self.action_tree.column("Delay(ms)", width=80, anchor=tk.CENTER)
        for c in columns:
            self.action_tree.heading(c, text=c)

        tree_scroll = ttk.Scrollbar(act_inner, orient=tk.VERTICAL,
                                    command=self.action_tree.yview)
        self.action_tree.config(yscrollcommand=tree_scroll.set)
        self.action_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.action_tree.bind("<Double-Button-1>", self._edit_action_dblclick)

        # Action toolbar
        act_btn = ttk.Frame(act_lf)
        act_btn.pack(fill=tk.X, pady=(2, 0))
        ttk.Button(act_btn, text="Edit", command=self._edit_action).pack(side=tk.LEFT, padx=1)
        ttk.Button(act_btn, text="Delete", command=self._delete_actions).pack(side=tk.LEFT, padx=1)
        ttk.Button(act_btn, text="Up", command=lambda: self._move_action(-1)).pack(side=tk.LEFT, padx=1)
        ttk.Button(act_btn, text="Down", command=lambda: self._move_action(1)).pack(side=tk.LEFT, padx=1)

        # -- Quick Tools notebook --
        tools_nb = ttk.Notebook(right_frame)
        tools_nb.pack(fill=tk.X, pady=(2, 0))

        # Tab 1: Type Text
        type_frame = ttk.Frame(tools_nb, padding=4)
        tools_nb.add(type_frame, text="Type Text")
        trow1 = ttk.Frame(type_frame)
        trow1.pack(fill=tk.X, pady=1)
        ttk.Label(trow1, text="Text:").pack(side=tk.LEFT, padx=(0, 4))
        self.text_input = ttk.Entry(trow1, width=40)
        self.text_input.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(trow1, text="Delay(ms):").pack(side=tk.LEFT, padx=(0, 4))
        self.text_delay_var = tk.StringVar(value="15")
        ttk.Entry(trow1, textvariable=self.text_delay_var, width=6).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(trow1, text="Insert Text", command=self._insert_typed_text).pack(side=tk.LEFT)

        # Tab 2: Special Keys
        spc_frame = ttk.Frame(tools_nb, padding=4)
        tools_nb.add(spc_frame, text="Special Keys")
        self._build_key_grid(spc_frame, [
            ("CTRL", "mod"), ("SHIFT", "mod"), ("ALT", "mod"), ("GUI", "mod"),
            ("ENTER", "spec"), ("TAB", "spec"), ("ESC", "spec"), ("BACKSPACE", "spec"),
            ("SPACE", "spec"), ("DEL", "spec"), ("HOME", "spec"), ("END", "spec"),
            ("INS", "spec"), ("PGUP", "spec"), ("PGDN", "spec"), ("CAPS", "spec"),
            ("PRINTSCREEN", "spec"), ("SCROLLLOCK", "spec"), ("PAUSE", "spec"),
            ("MENU", "spec"), ("POWER", "spec"), ("UNDO", "edit"), ("CUT", "edit"),
            ("COPY", "edit"), ("PASTE", "edit"), ("FIND", "edit"),
        ], columns=4)

        # Tab 3: Function & Arrow Keys
        fkey_frame = ttk.Frame(tools_nb, padding=4)
        tools_nb.add(fkey_frame, text="F / Arrow Keys")
        self._build_key_grid(fkey_frame, [
            ("F1", "fkey"), ("F2", "fkey"), ("F3", "fkey"), ("F4", "fkey"),
            ("F5", "fkey"), ("F6", "fkey"), ("F7", "fkey"), ("F8", "fkey"),
            ("F9", "fkey"), ("F10", "fkey"), ("F11", "fkey"), ("F12", "fkey"),
            ("F13", "fkey"), ("F14", "fkey"), ("F15", "fkey"), ("F16", "fkey"),
            ("F17", "fkey"), ("F18", "fkey"), ("F19", "fkey"), ("F20", "fkey"),
            ("F21", "fkey"), ("F22", "fkey"), ("F23", "fkey"), ("F24", "fkey"),
            ("UP", "arrow"), ("DOWN", "arrow"), ("LEFT", "arrow"), ("RIGHT", "arrow"),
        ], columns=4)

        # Tab 4: Media Keys
        media_frame = ttk.Frame(tools_nb, padding=4)
        tools_nb.add(media_frame, text="Media Keys")
        self._build_key_grid(media_frame, [
            ("VOL_UP", "media"), ("VOL_DOWN", "media"), ("MUTE", "media"),
            ("PLAY_PAUSE", "media"), ("NEXT", "media"), ("PREV", "media"),
            ("STOP", "media"), ("CALC", "media"), ("MAIL", "media"),
            ("WWW_SEARCH", "media"), ("WWW_HOME", "media"),
            ("WWW_BACK", "media"), ("WWW_FORWARD", "media"),
            ("WWW_REFRESH", "media"), ("WWW_STOP", "media"), ("WWW_FAVORITES", "media"),
            ("BRIGHTNESS_UP", "media"), ("BRIGHTNESS_DN", "media"),
            ("POWER_DOWN", "media"), ("SLEEP", "media"), ("WAKE", "media"),
            ("MEDIA_SELECT", "media"), ("AL_CC", "media"), ("AC_BOOKMARKS", "media"),
        ], columns=3)

        # Tab 5: Keypad
        kp_frame = ttk.Frame(tools_nb, padding=4)
        tools_nb.add(kp_frame, text="Keypad")
        self._build_key_grid(kp_frame, [
            ("NUMLOCK", "kp"), ("KP_SLASH", "kp"), ("KP_ASTERISK", "kp"), ("KP_MINUS", "kp"),
            ("KP_7", "kp"), ("KP_8", "kp"), ("KP_9", "kp"), ("KP_PLUS", "kp"),
            ("KP_4", "kp"), ("KP_5", "kp"), ("KP_6", "kp"), ("KP_ENTER", "kp"),
            ("KP_1", "kp"), ("KP_2", "kp"), ("KP_3", "kp"), ("KP_DOT", "kp"),
            ("KP_0", "kp"),
        ], columns=4)

        # Tab 6: Combo Key
        combo_frame = ttk.Frame(tools_nb, padding=4)
        tools_nb.add(combo_frame, text="Combo Key")
        crow1 = ttk.Frame(combo_frame)
        crow1.pack(fill=tk.X, pady=2)
        ttk.Label(crow1, text="Modifiers:").pack(side=tk.LEFT, padx=(0, 8))
        self.combo_ctrl = tk.BooleanVar()
        self.combo_shift = tk.BooleanVar()
        self.combo_alt = tk.BooleanVar()
        self.combo_gui = tk.BooleanVar()
        for var, name in [(self.combo_ctrl, "Ctrl"),
                          (self.combo_shift, "Shift"),
                          (self.combo_alt, "Alt"),
                          (self.combo_gui, "Gui")]:
            ttk.Checkbutton(crow1, text=name, variable=var).pack(side=tk.LEFT, padx=4)
        crow2 = ttk.Frame(combo_frame)
        crow2.pack(fill=tk.X, pady=2)
        ttk.Label(crow2, text="Key:").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_key_var = tk.StringVar()
        non_mod_keys = [k for k, v in KEY_DEFS.items()
                        if v["type"] not in ("modifier", "consumer")]
        ttk.Combobox(crow2, textvariable=self.combo_key_var,
                     values=non_mod_keys, width=10).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Label(crow2, text="Hold(ms):").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_hold_var = tk.StringVar(value="15")
        ttk.Entry(crow2, textvariable=self.combo_hold_var, width=6).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(crow2, text="Insert Combo", command=self._insert_combo).pack(side=tk.LEFT)

        # Tab 7: Record
        if HAS_PYNPUT:
            rec_frame = ttk.Frame(tools_nb, padding=4)
            tools_nb.add(rec_frame, text="Record")
            rrow = ttk.Frame(rec_frame)
            rrow.pack(fill=tk.X, pady=4)
            self.rec_btn = ttk.Button(rrow, text="Start Recording",
                                      command=self._toggle_recording)
            self.rec_btn.pack(side=tk.LEFT, padx=4)
            self.rec_status = ttk.Label(rrow, text="Idle")
            self.rec_status.pack(side=tk.LEFT, padx=8)
            self.rec_count = ttk.Label(rrow, text="Events: 0")
            self.rec_count.pack(side=tk.LEFT, padx=8)
        else:
            no_rec = ttk.Frame(tools_nb, padding=4)
            tools_nb.add(no_rec, text="Record")
            ttk.Label(no_rec, text="pynput not installed. Run: pip install pynput",
                      foreground="#f44336").pack(pady=8)

        # Status Bar
        status = ttk.Frame(self.root)
        status.pack(fill=tk.X, padx=4, pady=(0, 2))
        self.status_label = ttk.Label(status, text="Ready - No file loaded")
        self.status_label.pack(side=tk.LEFT)
        ttk.Label(status, text=f"Keys: {len(KEY_DEFS)}").pack(side=tk.RIGHT)

        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self._new_document())
        self.root.bind("<Control-o>", lambda e: self._load_xml())
        self.root.bind("<Control-s>", lambda e: self._save_xml())
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_key_grid(self, parent, keys, columns=4):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)
        colors = {"mod": "#d5d5d5", "spec": "#e0e0e0", "fkey": "#e8e8e8",
                  "arrow": "#d8dce8", "media": "#d0dae8",
                  "edit": "#e0e0d0", "kp": "#d8e8d8"}
        for i, (key_name, category) in enumerate(keys):
            row = i // columns
            col = i % columns
            bg = colors.get(category, "#e0e0e0")
            btn = tk.Button(frame, text=key_name, bg=bg, fg="#000000",
                            font=("Consolas", 8, "bold"), relief=tk.FLAT,
                            activebackground="#c0c0c0",
                            command=lambda k=key_name: self._insert_single_key(k))
            btn.grid(row=row, column=col, padx=1, pady=1, sticky="ew")
            frame.grid_columnconfigure(col, weight=1, uniform="kg")

    # ============================================
    # Trigger Key Selection (keyboard widget)
    # ============================================
    def _on_trigger_select(self, trigger_name):
        if self.current_macro is not None and self.current_macro >= 0:
            m = self.macros[self.current_macro]
            m.trigger_id = trigger_name
            self.trigger_display.config(text=trigger_name, foreground="#000000")
            self._refresh_list(select_idx=self.current_macro)
            self._update_assigned_keys()

    # ============================================
    # Document Management
    # ============================================
    def _new_document(self):
        if self.macros and not self._confirm_discard():
            return
        self.macros = []
        self.current_macro = -1
        self.current_file = None
        self._refresh_list()
        self._clear_editor()
        self._update_status("New document")

    def _update_status(self, msg):
        self.status_label.config(text=msg)

    # ============================================
    # Macro List Operations
    # ============================================
    def _refresh_list(self, select_idx=None):
        self.macro_listbox.delete(0, tk.END)
        for m in self.macros:
            label = f"{m.trigger_id:6s} -> {m.name}"
            if m.is_consumer:
                label += "  [media]"
            if m.repeat == "hold":
                label += "  [hold]"
            self.macro_listbox.insert(tk.END, label)
        if select_idx is not None and 0 <= select_idx < len(self.macros):
            self.macro_listbox.selection_set(select_idx)
            self.macro_listbox.activate(select_idx)
            self.current_macro = select_idx
            self._load_macro_to_editor(self.macros[select_idx])
        self._update_assigned_keys()

    def _on_macro_select(self, event):
        sel = self.macro_listbox.curselection()
        if sel:
            self._save_editor_to_macro()
            idx = sel[0]
            self.current_macro = idx
            self._load_macro_to_editor(self.macros[idx])
            self._update_assigned_keys()

    def _new_macro(self):
        m = Macro(trigger_id=TRIGGER_KEYS[0] if TRIGGER_KEYS else "A",
                  name="NewMacro")
        self.macros.append(m)
        idx = len(self.macros) - 1
        self._refresh_list(select_idx=idx)

    def _delete_macro(self):
        if self.current_macro is None or self.current_macro < 0:
            return
        if not messagebox.askyesno("Delete Macro",
                                   f"Delete '{self.macros[self.current_macro].name}'?"):
            return
        del self.macros[self.current_macro]
        new_idx = min(self.current_macro, len(self.macros) - 1)
        self.current_macro = -1
        self._refresh_list(select_idx=new_idx if new_idx >= 0 else None)
        if not self.macros:
            self._clear_editor()

    def _duplicate_macro(self):
        if self.current_macro is None or self.current_macro < 0:
            return
        self._save_editor_to_macro()
        orig = self.macros[self.current_macro]
        dup = Macro(trigger_id=orig.trigger_id,
                    name=orig.name + " (copy)",
                    is_consumer=orig.is_consumer,
                    repeat=orig.repeat)
        dup.actions = [a.copy() for a in orig.actions]
        self.macros.insert(self.current_macro + 1, dup)
        self._refresh_list(select_idx=self.current_macro + 1)

    def _move_macro_up(self):
        if self.current_macro is None or self.current_macro <= 0:
            return
        self._save_editor_to_macro()
        idx = self.current_macro
        self.macros[idx - 1], self.macros[idx] = self.macros[idx], self.macros[idx - 1]
        self._refresh_list(select_idx=idx - 1)

    def _move_macro_down(self):
        if self.current_macro is None or self.current_macro < 0:
            return
        if self.current_macro >= len(self.macros) - 1:
            return
        self._save_editor_to_macro()
        idx = self.current_macro
        self.macros[idx], self.macros[idx + 1] = self.macros[idx + 1], self.macros[idx]
        self._refresh_list(select_idx=idx + 1)

    # ============================================
    # Editor <-> Macro Data
    # ============================================
    def _load_macro_to_editor(self, macro):
        self.trigger_display.config(text=macro.trigger_id, foreground="#000000")
        self.kb_selector.set_selected(macro.trigger_id)
        self.name_var.set(macro.name)
        self.consumer_var.set(macro.is_consumer)
        self.repeat_var.set(macro.repeat if macro.repeat else "none")
        self._refresh_action_tree(macro)
        self.action_count_label.config(text=str(macro.total_actions()))

    def _save_editor_to_macro(self):
        if self.current_macro is None or self.current_macro < 0:
            return
        if self.current_macro >= len(self.macros):
            return
        m = self.macros[self.current_macro]
        selected = self.kb_selector.get_selected()
        if selected:
            m.trigger_id = selected
        m.name = self.name_var.get()
        m.is_consumer = self.consumer_var.get()
        r = self.repeat_var.get()
        m.repeat = r if r != "none" else None

    def _clear_editor(self):
        self.trigger_display.config(text="(click keyboard below)", foreground="#888888")
        self.kb_selector.set_selected(None)
        self.name_var.set("")
        self.consumer_var.set(False)
        self.repeat_var.set("none")
        self.action_tree.delete(*self.action_tree.get_children())
        self.action_count_label.config(text="0")
        self.current_macro = -1

    def _on_setting_change(self, event=None):
        if self.current_macro is not None and self.current_macro >= 0:
            self._save_editor_to_macro()
            self._refresh_list(select_idx=self.current_macro)

    def _update_assigned_keys(self):
        """Refresh keyboard widget to highlight keys that have macros."""
        assigned = {m.trigger_id for m in self.macros if m.trigger_id}
        self.kb_selector.set_assigned_keys(assigned)

    # ============================================
    # Action Tree Operations
    # ============================================
    def _refresh_action_tree(self, macro):
        self.action_tree.delete(*self.action_tree.get_children())
        for i, a in enumerate(macro.actions):
            group_str = str(a.group) if a.group is not None else ""
            self.action_tree.insert("", tk.END, iid=str(i),
                                    values=(i, a.key_name, group_str,
                                            a.action_type, a.delay))

    def _add_actions(self, new_actions):
        if self.current_macro is None or self.current_macro < 0:
            return -1
        m = self.macros[self.current_macro]
        start_idx = len(m.actions)
        m.actions.extend(new_actions)
        self._refresh_action_tree(m)
        self.action_count_label.config(text=str(m.total_actions()))
        return start_idx

    def _edit_action(self):
        sel = self.action_tree.selection()
        if not sel:
            return
        self._edit_action_dblclick(None)

    def _edit_action_dblclick(self, event):
        sel = self.action_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if self.current_macro is None:
            return
        m = self.macros[self.current_macro]
        if idx >= len(m.actions):
            return
        a = m.actions[idx]

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Edit Action #{idx}")
        dlg.geometry("320x210")
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.configure(bg="#ffffff")

        ttk.Label(dlg, text="Key:").grid(row=0, column=0, padx=8, pady=4, sticky="w")
        key_var = tk.StringVar(value=a.key_name)
        ttk.Combobox(dlg, textvariable=key_var,
                     values=list(KEY_DEFS.keys()), width=15).grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(dlg, text="Group:").grid(row=1, column=0, padx=8, pady=4, sticky="w")
        group_var = tk.StringVar(value=str(a.group) if a.group is not None else "")
        ttk.Entry(dlg, textvariable=group_var, width=8).grid(row=1, column=1, padx=4, pady=4, sticky="w")

        ttk.Label(dlg, text="Type:").grid(row=2, column=0, padx=8, pady=4, sticky="w")
        type_var = tk.StringVar(value=a.action_type)
        ttk.Combobox(dlg, textvariable=type_var,
                     values=["make", "break"], width=10,
                     state="readonly").grid(row=2, column=1, padx=4, pady=4)

        ttk.Label(dlg, text="Delay(ms):").grid(row=3, column=0, padx=8, pady=4, sticky="w")
        dly_var = tk.StringVar(value=str(a.delay))
        ttk.Entry(dlg, textvariable=dly_var, width=8).grid(row=3, column=1, padx=4, pady=4)

        def apply():
            a.key_name = key_var.get()
            a.action_type = type_var.get()
            try:
                a.delay = int(dly_var.get())
            except ValueError:
                a.delay = 15
            g = group_var.get().strip()
            try:
                a.group = int(g) if g else None
            except ValueError:
                a.group = None
            self._refresh_action_tree(m)
            dlg.destroy()

        ttk.Button(dlg, text="OK", command=apply).grid(row=4, column=0,
                                                        columnspan=2, pady=12)

    def _delete_actions(self):
        sel = self.action_tree.selection()
        if not sel or self.current_macro is None:
            return
        m = self.macros[self.current_macro]
        indices = sorted([int(s) for s in sel], reverse=True)
        for i in indices:
            if 0 <= i < len(m.actions):
                del m.actions[i]
        self._refresh_action_tree(m)
        self.action_count_label.config(text=str(m.total_actions()))

    def _move_action(self, direction):
        sel = self.action_tree.selection()
        if not sel or self.current_macro is None:
            return
        m = self.macros[self.current_macro]
        idx = int(sel[0])
        new_idx = idx + direction
        if 0 <= new_idx < len(m.actions):
            m.actions[idx], m.actions[new_idx] = m.actions[new_idx], m.actions[idx]
            self._refresh_action_tree(m)
            self.action_tree.selection_set(str(new_idx))

    # ============================================
    # Quick Tools: Insertions
    # ============================================
    def _insert_single_key(self, key_name):
        if self.current_macro is None or self.current_macro < 0:
            messagebox.showwarning("No Macro", "Create a macro first (click + New)")
            return
        actions = [
            MacroAction(key_name, "make", 15),
            MacroAction(key_name, "break", 15),
        ]
        self._add_actions(actions)

    def _insert_typed_text(self):
        if self.current_macro is None or self.current_macro < 0:
            messagebox.showwarning("No Macro", "Create a macro first (click + New)")
            return
        text = self.text_input.get()
        if not text:
            return
        try:
            delay_ms = int(self.text_delay_var.get())
        except ValueError:
            delay_ms = 15

        actions = []
        for ch in text:
            if ch == ' ':
                actions.append(MacroAction("SPACE", "make", 15))
                actions.append(MacroAction("SPACE", "break", delay_ms))
            elif ch in '\n\r':
                actions.append(MacroAction("ENTER", "make", 15))
                actions.append(MacroAction("ENTER", "break", delay_ms))
            elif 'a' <= ch <= 'z':
                key = ch.upper()
                actions.append(MacroAction(key, "make", 15))
                actions.append(MacroAction(key, "break", delay_ms))
            elif 'A' <= ch <= 'Z':
                actions.append(MacroAction("SHIFT", "make", 15))
                actions.append(MacroAction(ch, "make", 15))
                actions.append(MacroAction(ch, "break", delay_ms))
                actions.append(MacroAction("SHIFT", "break", 15))
            elif '0' <= ch <= '9':
                actions.append(MacroAction(ch, "make", 15))
                actions.append(MacroAction(ch, "break", delay_ms))

        if actions:
            self._add_actions(actions)

    def _insert_combo(self):
        if self.current_macro is None or self.current_macro < 0:
            messagebox.showwarning("No Macro", "Create a macro first (click + New)")
            return
        key = self.combo_key_var.get()
        if not key:
            return
        try:
            hold_ms = int(self.combo_hold_var.get())
        except ValueError:
            hold_ms = 15

        modifiers = []
        if self.combo_ctrl.get(): modifiers.append("CTRL")
        if self.combo_shift.get(): modifiers.append("SHIFT")
        if self.combo_alt.get(): modifiers.append("ALT")
        if self.combo_gui.get(): modifiers.append("GUI")

        actions = []
        for mod in modifiers:
            actions.append(MacroAction(mod, "make", 15))
        actions.append(MacroAction(key, "make", 15))
        actions.append(MacroAction(key, "break", hold_ms))
        for mod in reversed(modifiers):
            actions.append(MacroAction(mod, "break", 15))
        self._add_actions(actions)

    # ============================================
    # Recording (pynput)
    # ============================================
    def _toggle_recording(self):
        if not HAS_PYNPUT:
            messagebox.showerror("Error", "pynput not installed.\nRun: pip install pynput")
            return
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self):
        if self.current_macro is None or self.current_macro < 0:
            messagebox.showwarning("No Macro", "Create a macro first (click + New)")
            return
        self._recording = True
        self._recorded_events = []
        self._rec_start_time = time.time()
        self.rec_btn.config(text="Stop Recording", style="Rec.TButton")
        self.rec_status.config(text="RECORDING...", foreground="#f44336")
        self._rec_thread = threading.Thread(target=self._record_loop, daemon=True)
        self._rec_thread.start()

    def _stop_recording(self):
        self._recording = False
        self.rec_btn.config(text="Start Recording", style="TButton")
        self.rec_status.config(text="Processing...")
        if not self._recorded_events:
            self.rec_status.config(text="No events recorded")
            return
        actions = []
        active_keys = {}
        for ts, key_name, is_press in self._recorded_events:
            if is_press:
                active_keys[key_name] = ts
                actions.append(MacroAction(key_name, "make", 15))
            else:
                if key_name in active_keys:
                    hold_duration = int((ts - active_keys[key_name]) * 1000)
                    del active_keys[key_name]
                    delay = max(15, hold_duration)
                    actions.append(MacroAction(key_name, "break", delay))
                else:
                    actions.append(MacroAction(key_name, "break", 15))
        if actions:
            self._add_actions(actions)
            self.rec_status.config(
                text=f"{len(actions)} actions from {len(self._recorded_events)} events",
                foreground="#4caf50")
        else:
            self.rec_status.config(text="No actions generated")
        self.rec_count.config(text=f"Events: {len(self._recorded_events)}")

    def _record_loop(self):
        try:
            from pynput.keyboard import Listener as KbListener
        except ImportError:
            return

        def on_press(key):
            if not self._recording:
                return False
            ts = time.time() - self._rec_start_time
            key_name = self._pynput_to_name(key)
            if key_name:
                self._recorded_events.append((ts, key_name, True))

        def on_release(key):
            if not self._recording:
                return False
            ts = time.time() - self._rec_start_time
            key_name = self._pynput_to_name(key)
            if key_name:
                self._recorded_events.append((ts, key_name, False))

        with KbListener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    def _pynput_to_name(self, key):
        if key in PYNPUT_KEY_MAP:
            return PYNPUT_KEY_MAP[key]
        try:
            ch = key.char
            if ch is None:
                return None
            if 'a' <= ch <= 'z':
                return ch.upper()
            if 'A' <= ch <= 'Z':
                return ch
            if '0' <= ch <= '9':
                return ch
        except AttributeError:
            pass
        return None

    # ============================================
    # XML I/O
    # ============================================
    def _save_xml(self, event=None):
        self._save_editor_to_macro()
        if not self.current_file:
            return self._save_xml_as()
        self._write_xml_file(self.current_file)

    def _save_xml_as(self):
        self._save_editor_to_macro()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
            title="Save XML File")
        if filepath:
            self.current_file = filepath
            self._write_xml_file(filepath)

    def _write_xml_file(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<ComboKey>\n')
                for i, m in enumerate(self.macros):
                    if i > 0:
                        f.write('\n')
                    f.write(m.to_xml_string())
                    f.write('\n')
                f.write('</ComboKey>\n')
            filename = os.path.basename(filepath)
            self._update_status(f"Saved: {filename} ({len(self.macros)} macros)")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _export_image(self):
        """Export a keyboard layout image showing all macro trigger keys."""
        self._save_editor_to_macro()

        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            messagebox.showerror(
                "Missing Pillow",
                "Pillow is required for image export.\n\n"
                "Install it with:  pip install Pillow")
            return

        # Build trigger -> macro name map
        trigger_map = {}
        for m in self.macros:
            if m.trigger_id:
                trigger_map[m.trigger_id] = m.name

        # Drawing constants
        KEY_W   = 66
        KEY_H   = 54
        GAP     = 4
        MARGIN  = 16
        TITLE_H = 40
        COL_NORM  = (224, 224, 224)
        COL_ASSN  = (179, 224, 247)
        COL_DIS   = (160, 160, 160)
        COL_BDR   = (100, 100, 100)
        COL_TXT   = (0, 0, 0)
        COL_DIS_T = (102, 102, 102)
        COL_MACRO = (0, 80, 160)
        BG        = (255, 255, 255)

        # Image size
        max_cols = max(len(row) for row in KEYBOARD_LAYOUT)
        kb_w = max_cols * (KEY_W + GAP) - GAP
        kb_h = len(KEYBOARD_LAYOUT) * (KEY_H + GAP) - GAP
        img_w = kb_w + MARGIN * 2
        img_h = TITLE_H + kb_h + MARGIN * 2 + 8

        img = Image.new("RGB", (img_w, img_h), BG)
        draw = ImageDraw.Draw(img)

        # Fonts — use Microsoft YaHei for CJK + Latin support
        def _char_w(ch):
            """CJK chars count as 2, others as 1."""
            cp = ord(ch)
            return 2 if (0x4E00 <= cp <= 0x9FFF or
                         0x3400 <= cp <= 0x4DBF or
                         0xF900 <= cp <= 0xFAFF or
                         0x3000 <= cp <= 0x303F or
                         0xFF00 <= cp <= 0xFFEF) else 1

        def _wrap_text(text, max_w=8, max_lines=2):
            """Wrap text by display width (CJK=2, ASCII=1). Max 2 lines, 16 total."""
            lines = []
            cur = ""
            cur_w = 0
            for ch in text:
                cw = _char_w(ch)
                if cur_w + cw > max_w:
                    lines.append(cur)
                    if len(lines) >= max_lines:
                        return lines
                    cur = ch
                    cur_w = cw
                else:
                    cur += ch
                    cur_w += cw
            if cur:
                lines.append(cur)
            return lines[:max_lines]

        def _load_font(size):
            for path in [
                "C:/Windows/Fonts/msyh.ttc",   # 微软雅黑
                "C:/Windows/Fonts/msyhbd.ttc",  # 微软雅黑 粗体
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/arial.ttf",
            ]:
                try:
                    return ImageFont.truetype(path, size)
                except (OSError, IOError):
                    continue
            return ImageFont.load_default()

        font_key   = _load_font(15)
        font_macro = _load_font(12)
        font_title = _load_font(18)

        # Title (XML filename)
        title = os.path.basename(self.current_file) if self.current_file else "Untitled"
        draw.text((MARGIN, 8), title, fill=COL_TXT, font=font_title)

        # Draw keyboard
        y0 = TITLE_H + MARGIN
        for row in KEYBOARD_LAYOUT:
            x0 = MARGIN
            for label, trigger_name in row:
                x1, y1 = x0 + KEY_W, y0 + KEY_H

                if trigger_name is None:
                    fill, txt_c = COL_DIS, COL_DIS_T
                elif trigger_name in trigger_map:
                    fill, txt_c = COL_ASSN, COL_TXT
                else:
                    fill, txt_c = COL_NORM, COL_TXT

                draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=fill, outline=COL_BDR)

                # Key label: single letters uppercase, others as-is
                display_label = label.upper() if len(label) == 1 and label.isalpha() else label
                draw.text((x0 + 4, y0 + 4), display_label, fill=txt_c, font=font_key)

                # Macro name on assigned keys (auto-wrap, max 2 lines)
                if trigger_name and trigger_name in trigger_map:
                    lines = _wrap_text(trigger_map[trigger_name])
                    line_h = 14
                    start_y = y0 + KEY_H - 4 - len(lines) * line_h
                    for li, line in enumerate(lines):
                        draw.text((x0 + 4, start_y + li * line_h),
                                  line, fill=COL_MACRO, font=font_macro)

                x0 += KEY_W + GAP
            y0 += KEY_H + GAP

        # Save dialog
        default_name = os.path.splitext(title)[0] + ".png"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG Image", "*.png"), ("All files", "*.*")],
            title="Export Image")
        if save_path:
            try:
                img.save(save_path)
                self._update_status(f"Exported: {os.path.basename(save_path)}")
            except Exception as e:
                messagebox.showerror("Export Error", str(e))

    def _load_xml(self, event=None):
        if self.macros and not self._confirm_discard():
            return
        filepath = filedialog.askopenfilename(
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
            title="Open XML File")
        if not filepath:
            return
        try:
            self.macros = []
            tree = ET.parse(filepath)
            root = tree.getroot()
            for key_elem in root.findall("Key"):
                m = Macro()
                m.trigger_id = key_elem.get("id", "")
                m.name = key_elem.get("name", "Unnamed")
                m.is_consumer = (key_elem.get("type", "").lower() == "consumer")
                repeat_val = key_elem.get("repeat", "")
                m.repeat = repeat_val if repeat_val else None
                for act_elem in key_elem.findall("Action"):
                    group_str = act_elem.get("group", "")
                    group_val = int(group_str) if group_str.isdigit() else None
                    a = MacroAction(
                        key_name=act_elem.get("key", act_elem.get("keyCode", "?")),
                        action_type=act_elem.get("type", "make").lower(),
                        delay=int(act_elem.get("delay", "15")),
                        group=group_val)
                    m.actions.append(a)
                self.macros.append(m)
            self.current_file = filepath
            filename = os.path.basename(filepath)
            self.current_macro = -1
            self._refresh_list(select_idx=0 if self.macros else None)
            self._update_status(f"Loaded: {filename} ({len(self.macros)} macros)")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to parse XML:\n{e}")

    def _confirm_discard(self):
        return messagebox.askyesno("Discard Changes",
                                   "Discard current changes and continue?")

    def _on_close(self):
        if self.macros:
            self._save_editor_to_macro()
            if messagebox.askyesno("Exit", "Save before exit?"):
                self._save_xml()
        self.root.destroy()
