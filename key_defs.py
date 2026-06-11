"""Key definitions and keyboard layout data for CardPuter ComboKey Editor."""

from collections import OrderedDict

# All available output key names
KEY_DEFS = OrderedDict([
    # Modifiers (full names + short aliases)
    ("CTRL",    {"char": "Ct",  "type": "modifier", "hid": 0xE0}),
    ("Ctrl",    {"char": "Ct",  "type": "modifier", "hid": 0xE0}),
    ("SHIFT",   {"char": "Sht", "type": "modifier", "hid": 0xE1}),
    ("Sht",     {"char": "Sht", "type": "modifier", "hid": 0xE1}),
    ("ALT",     {"char": "Al",  "type": "modifier", "hid": 0xE2}),
    ("Opt",     {"char": "Op",  "type": "modifier", "hid": 0xE4}),
    ("GUI",     {"char": "Gui", "type": "modifier", "hid": 0xE3}),
    ("Fn",      {"char": "Fn",  "type": "modifier", "hid": 0xE3}),

    # Letters
    *[(c, {"char": c, "type": "key", "hid": 0x04 + i})
      for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")],

    # Numbers
    ("0", {"char": "0", "type": "key", "hid": 0x27}),
    *[(str(n), {"char": str(n), "type": "key", "hid": 0x1E + n - 1})
      for n in range(1, 10)],

    # Function keys
    *[(f"F{n}", {"char": f"F{n}", "type": "key", "hid": 0x3A + n - 1})
      for n in range(1, 13)],
    ("F13", {"char": "F13", "type": "key", "hid": 0x68}),
    ("F14", {"char": "F14", "type": "key", "hid": 0x69}),
    ("F15", {"char": "F15", "type": "key", "hid": 0x6A}),
    ("F16", {"char": "F16", "type": "key", "hid": 0x6B}),
    ("F17", {"char": "F17", "type": "key", "hid": 0x6C}),
    ("F18", {"char": "F18", "type": "key", "hid": 0x6D}),
    ("F19", {"char": "F19", "type": "key", "hid": 0x6E}),
    ("F20", {"char": "F20", "type": "key", "hid": 0x6F}),
    ("F21", {"char": "F21", "type": "key", "hid": 0x70}),
    ("F22", {"char": "F22", "type": "key", "hid": 0x71}),
    ("F23", {"char": "F23", "type": "key", "hid": 0x72}),
    ("F24", {"char": "F24", "type": "key", "hid": 0x73}),

    # Special keys
    ("ENTER",     {"char": "Ent", "type": "key", "hid": 0x28}),
    ("RETURN",    {"char": "Ent", "type": "key", "hid": 0x28}),
    ("ESC",       {"char": "Esc", "type": "key", "hid": 0x29}),
    ("BACKSPACE", {"char": "BSp", "type": "key", "hid": 0x2A}),
    ("BSP",       {"char": "BSp", "type": "key", "hid": 0x2A}),
    ("TAB",       {"char": "Tab", "type": "key", "hid": 0x2B}),
    ("SPACE",     {"char": "Spc", "type": "key", "hid": 0x2C}),
    ("CAPS",      {"char": "Cap", "type": "key", "hid": 0x39}),
    ("INS",       {"char": "Ins", "type": "key", "hid": 0x49}),
    ("DEL",       {"char": "Del", "type": "key", "hid": 0x4C}),
    ("HOME",      {"char": "Hom", "type": "key", "hid": 0x4A}),
    ("END",       {"char": "End", "type": "key", "hid": 0x4D}),
    ("PGUP",      {"char": "PgU", "type": "key", "hid": 0x4B}),
    ("PGDN",      {"char": "PgD", "type": "key", "hid": 0x4E}),

    # Arrow keys
    ("UP",        {"char": "Up",  "type": "key", "hid": 0x52}),
    ("DOWN",      {"char": "Dn",  "type": "key", "hid": 0x51}),
    ("LEFT",      {"char": "Lf",  "type": "key", "hid": 0x50}),
    ("RIGHT",     {"char": "Rt",  "type": "key", "hid": 0x4F}),

    # System / Utility
    ("PRINTSCREEN", {"char": "PrS", "type": "key", "hid": 0x46}),
    ("SCROLLLOCK",  {"char": "ScL", "type": "key", "hid": 0x47}),
    ("PAUSE",       {"char": "Pau", "type": "key", "hid": 0x48}),
    ("MENU",        {"char": "Men", "type": "key", "hid": 0x65}),
    ("POWER",       {"char": "Pwr", "type": "key", "hid": 0x66}),

    # Keypad
    ("NUMLOCK",     {"char": "NLk", "type": "key", "hid": 0x53}),
    ("KP_SLASH",    {"char": "KP/", "type": "key", "hid": 0x54}),
    ("KP_ASTERISK", {"char": "KP*", "type": "key", "hid": 0x55}),
    ("KP_MINUS",    {"char": "KP-", "type": "key", "hid": 0x56}),
    ("KP_PLUS",     {"char": "KP+", "type": "key", "hid": 0x57}),
    ("KP_ENTER",    {"char": "KEn", "type": "key", "hid": 0x58}),
    ("KP_1", {"char": "K1", "type": "key", "hid": 0x59}),
    ("KP_2", {"char": "K2", "type": "key", "hid": 0x5A}),
    ("KP_3", {"char": "K3", "type": "key", "hid": 0x5B}),
    ("KP_4", {"char": "K4", "type": "key", "hid": 0x5C}),
    ("KP_5", {"char": "K5", "type": "key", "hid": 0x5D}),
    ("KP_6", {"char": "K6", "type": "key", "hid": 0x5E}),
    ("KP_7", {"char": "K7", "type": "key", "hid": 0x5F}),
    ("KP_8", {"char": "K8", "type": "key", "hid": 0x60}),
    ("KP_9", {"char": "K9", "type": "key", "hid": 0x61}),
    ("KP_0", {"char": "K0", "type": "key", "hid": 0x62}),
    ("KP_DOT",      {"char": "K.", "type": "key", "hid": 0x63}),

    # Edit keys
    ("UNDO",  {"char": "Und", "type": "key", "hid": 0x7A}),
    ("CUT",   {"char": "Cut", "type": "key", "hid": 0x7B}),
    ("COPY",  {"char": "Cop", "type": "key", "hid": 0x7C}),
    ("PASTE", {"char": "Pst", "type": "key", "hid": 0x7D}),
    ("FIND",  {"char": "Fnd", "type": "key", "hid": 0x7E}),

    # International keys
    ("NONUS_BSLASH", {"char": "\\2", "type": "key", "hid": 0x64}),
    ("INTL1", {"char": "Ro",  "type": "key", "hid": 0x87}),
    ("INTL2", {"char": "Kan", "type": "key", "hid": 0x88}),
    ("INTL3", {"char": "Yen", "type": "key", "hid": 0x89}),
    ("INTL4", {"char": "Hen", "type": "key", "hid": 0x8A}),
    ("INTL5", {"char": "Muh", "type": "key", "hid": 0x8B}),
    ("LANG1", {"char": "Lg1", "type": "key", "hid": 0x90}),
    ("LANG2", {"char": "Lg2", "type": "key", "hid": 0x91}),
    ("LANG3", {"char": "Lg3", "type": "key", "hid": 0x92}),
    ("LANG4", {"char": "Lg4", "type": "key", "hid": 0x93}),
    ("LANG5", {"char": "Lg5", "type": "key", "hid": 0x94}),

    # Punctuation (full names + symbol aliases)
    ("MINUS",     {"char": "-",  "type": "key", "hid": 0x2D}),
    ("-",         {"char": "-",  "type": "key", "hid": 0x2D}),
    ("EQUAL",     {"char": "=",  "type": "key", "hid": 0x2E}),
    ("=",         {"char": "=",  "type": "key", "hid": 0x2E}),
    ("LBRACKET",  {"char": "[",  "type": "key", "hid": 0x2F}),
    ("[",         {"char": "[",  "type": "key", "hid": 0x2F}),
    ("RBRACKET",  {"char": "]",  "type": "key", "hid": 0x30}),
    ("]",         {"char": "]",  "type": "key", "hid": 0x30}),
    ("BACKSLASH", {"char": "\\", "type": "key", "hid": 0x31}),
    ("\\",        {"char": "\\", "type": "key", "hid": 0x31}),
    ("SEMICOLON", {"char": ";",  "type": "key", "hid": 0x33}),
    (";",         {"char": ";",  "type": "key", "hid": 0x33}),
    ("QUOTE",     {"char": "'",  "type": "key", "hid": 0x34}),
    ("'",         {"char": "'",  "type": "key", "hid": 0x34}),
    ("BACKTICK",  {"char": "`",  "type": "key", "hid": 0x35}),
    ("`",         {"char": "`",  "type": "key", "hid": 0x35}),
    ("COMMA",     {"char": ",",  "type": "key", "hid": 0x36}),
    (",",         {"char": ",",  "type": "key", "hid": 0x36}),
    ("PERIOD",    {"char": ".",  "type": "key", "hid": 0x37}),
    (".",         {"char": ".",  "type": "key", "hid": 0x37}),
    ("SLASH",     {"char": "/",  "type": "key", "hid": 0x38}),
    ("/",         {"char": "/",  "type": "key", "hid": 0x38}),

    # Consumer (Media) keys
    ("VOL_UP",       {"char": "V+",  "type": "consumer", "hid": 0x00E9}),
    ("VOL_DOWN",     {"char": "V-",  "type": "consumer", "hid": 0x00EA}),
    ("MUTE",         {"char": "Mut", "type": "consumer", "hid": 0x00E2}),
    ("PLAY_PAUSE",   {"char": "Ply", "type": "consumer", "hid": 0x00CD}),
    ("NEXT",         {"char": "Nxt", "type": "consumer", "hid": 0x00B5}),
    ("PREV",         {"char": "Prv", "type": "consumer", "hid": 0x00B6}),
    ("STOP",         {"char": "Stp", "type": "consumer", "hid": 0x00B7}),
    ("CALC",         {"char": "Cal", "type": "consumer", "hid": 0x0192}),
    ("MAIL",         {"char": "Mal", "type": "consumer", "hid": 0x018A}),
    ("WWW_SEARCH",   {"char": "Src", "type": "consumer", "hid": 0x0221}),
    ("WWW_HOME",     {"char": "Hme", "type": "consumer", "hid": 0x0223}),
    ("POWER_DOWN",    {"char": "PwD", "type": "consumer", "hid": 0x0030}),
    ("SLEEP",         {"char": "Slp", "type": "consumer", "hid": 0x0032}),
    ("WAKE",          {"char": "Wak", "type": "consumer", "hid": 0x0033}),
    ("WWW_BACK",      {"char": "Wbk", "type": "consumer", "hid": 0x0224}),
    ("WWW_FORWARD",   {"char": "WfW", "type": "consumer", "hid": 0x0225}),
    ("WWW_REFRESH",   {"char": "Wrf", "type": "consumer", "hid": 0x0227}),
    ("WWW_STOP",      {"char": "Wst", "type": "consumer", "hid": 0x0226}),
    ("WWW_FAVORITES", {"char": "Wfv", "type": "consumer", "hid": 0x022A}),
    ("BRIGHTNESS_UP", {"char": "Br+", "type": "consumer", "hid": 0x006F}),
    ("BRIGHTNESS_DN", {"char": "Br-", "type": "consumer", "hid": 0x0070}),
    ("MEDIA_SELECT",  {"char": "Med", "type": "consumer", "hid": 0x0183}),
    ("AL_CC",         {"char": "Sub", "type": "consumer", "hid": 0x018C}),
    ("AC_BOOKMARKS",  {"char": "Bkm", "type": "consumer", "hid": 0x018D}),
])

# CardPuter trigger keys — physical keys usable as macro triggers
TRIGGER_KEYS = [
    "`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "BSP",
    "TAB", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\",
    "Sht", "A", "S", "D", "F", "G", "H", "J", "K", "L", "'", "ENTER",
    "Ctrl", "Opt", "Alt", "Z", "X", "C", "V", "B", "N", "M", "SPACE",
]

# Keyboard layout for graphical trigger key selector
# Each row: list of (display_label, trigger_key_name_or_None)
# None means the key cannot be selected as a trigger (grayed out)
KEYBOARD_LAYOUT = [
    # Row 1
    [
        ("`", "`"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"),
        ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9"),
        ("0", "0"), ("-", "-"), ("=", "="), ("BSP", "BSP"),
    ],
    # Row 2
    [
        ("TAB", "TAB"), ("q", "Q"), ("w", "W"), ("e", "E"), ("r", "R"),
        ("t", "T"), ("y", "Y"), ("u", "U"), ("i", "I"), ("o", "O"),
        ("p", "P"), ("[", "["), ("]", "]"), ("\\", "\\"),
    ],
    # Row 3
    [
        ("Fn", None), ("Sht", "Sht"), ("a", "A"), ("s", "S"), ("d", "D"),
        ("f", "F"), ("g", "G"), ("h", "H"), ("j", "J"), ("k", "K"),
        ("l", "L"), (";", None), ("'", "'"), ("ENTER", "ENTER"),
    ],
    # Row 4
    [
        ("Ctrl", "Ctrl"), ("Opt", "Opt"), ("Alt", "Alt"),
        ("z", "Z"), ("x", "X"), ("c", "C"), ("v", "V"),
        ("b", "B"), ("n", "N"), ("m", "M"),
        (",", None), (".", None), ("/", None), ("SPACE", "SPACE"),
    ],
]

# pynput → our key name mapping (for recording)
PYNPUT_KEY_MAP = {}
try:
    from pynput.keyboard import Key, KeyCode
    PYNPUT_KEY_MAP = {
        Key.ctrl_l: "CTRL",  Key.ctrl_r: "CTRL",
        Key.shift_l: "SHIFT", Key.shift_r: "SHIFT",
        Key.alt_l: "ALT",   Key.alt_r: "ALT",
        Key.cmd_l: "GUI",   Key.cmd_r: "GUI",
        Key.enter: "ENTER", Key.tab: "TAB",
        Key.esc: "ESC",     Key.space: "SPACE",
        Key.backspace: "BACKSPACE",
        Key.delete: "DEL",  Key.insert: "INS",
        Key.home: "HOME",   Key.end: "END",
        Key.page_up: "PGUP", Key.page_down: "PGDN",
        Key.up: "UP",       Key.down: "DOWN",
        Key.left: "LEFT",   Key.right: "RIGHT",
        Key.caps_lock: "CAPS",
        Key.f1: "F1", Key.f2: "F2", Key.f3: "F3", Key.f4: "F4",
        Key.f5: "F5", Key.f6: "F6", Key.f7: "F7", Key.f8: "F8",
        Key.f9: "F9", Key.f10: "F10", Key.f11: "F11", Key.f12: "F12",
        Key.f13: "F13", Key.f14: "F14", Key.f15: "F15", Key.f16: "F16",
        Key.f17: "F17", Key.f18: "F18", Key.f19: "F19", Key.f20: "F20",
        Key.f21: "F21", Key.f22: "F22", Key.f23: "F23", Key.f24: "F24",
        Key.print_screen: "PRINTSCREEN", Key.scroll_lock: "SCROLLLOCK",
        Key.pause: "PAUSE", Key.menu: "MENU",
        Key.num_lock: "NUMLOCK",
    }
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False
