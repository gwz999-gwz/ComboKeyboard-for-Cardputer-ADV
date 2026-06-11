"""Data models for ComboKey macros."""


class MacroAction:
    """Single action in a macro sequence."""

    def __init__(self, key_name, action_type, delay=15, group=None):
        self.key_name = key_name
        self.action_type = action_type  # "make" or "break"
        self.delay = delay
        self.group = group              # group id (int) or None

    def to_xml(self):
        group_attr = f' group="{self.group}"' if self.group is not None else ""
        return (f'    <Action key="{self.key_name}"{group_attr} '
                f'type="{self.action_type}" '
                f'delay="{self.delay}" />')

    def display_str(self):
        return f"{self.key_name:12s} {self.action_type:5s}  {self.delay}ms"

    def copy(self):
        return MacroAction(self.key_name, self.action_type, self.delay, self.group)


class Macro:
    """Complete macro: trigger key + sequence of actions."""

    def __init__(self, trigger_id="", name="", is_consumer=False, repeat=None):
        self.trigger_id = trigger_id
        self.name = name
        self.is_consumer = is_consumer
        self.repeat = repeat        # None or "hold"
        self.actions = []

    def add_make_break(self, key_name, hold_ms=15, pre_delay=15):
        self.actions.append(MacroAction(key_name, "make", pre_delay))
        self.actions.append(MacroAction(key_name, "break", hold_ms))

    def to_xml_string(self):
        lines = []
        attrs = []
        if self.is_consumer:
            attrs.append('type="consumer"')
        if self.repeat:
            attrs.append(f'repeat="{self.repeat}"')
        attr_str = " " + " ".join(attrs) if attrs else ""
        lines.append(f'  <Key id="{self.trigger_id}" name="{self.name}"{attr_str}>')
        for a in self.actions:
            lines.append(a.to_xml())
        lines.append('  </Key>')
        return '\n'.join(lines)

    def total_actions(self):
        return len(self.actions)
