import time
import re
from typing import List, Any, Dict

from .gui import AilaGUI
from .parser import Parser


class AilaInterpreter:
    """Simple line-oriented interpreter for the Aila language."""

    def __init__(self) -> None:
        self.gui = AilaGUI()
        self.window_created = False
        self.variables: Dict[str, Any] = {}

    def _require_window(self) -> None:
        if not self.window_created:
            self.gui.create_window("Aila")
            self.window_created = True

    def _substitute_vars(self, args: List[str]) -> List[str]:
        """Substitutes variable references in a list of arguments."""
        substituted_args = []
        for arg in args:
            # Use a regex to find all occurrences of $varname
            # and replace them using a lambda function.
            def replace_match(match):
                var_name = match.group(1)
                return str(self.variables.get(var_name, f"${var_name}"))

            substituted_arg = re.sub(r'\$([a-zA-Z_][a-zA-Z0-9_]*)', replace_match, arg)
            substituted_args.append(substituted_arg)
        return substituted_args

    def _get_numeric_value(self, value: str) -> float | int | None:
        """Converts a string to a float or int, returns None if not possible."""
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return None

    def execute(self, source: str) -> None:
        """Executes a script from a source string."""
        parser = Parser(source)
        commands = parser.parse()

        for cmd in commands:
            # Substitute variables in arguments before executing the command
            cmd.args = self._substitute_vars(cmd.args)

            if cmd.name == "say":
                print(" ".join(cmd.args))

            elif cmd.name == "set":
                if len(cmd.args) != 2:
                    print(f"L{cmd.line_number}: 'set' requires 2 arguments.")
                    continue
                var_name, value = cmd.args
                # Try to convert to number, otherwise store as string
                numeric_value = self._get_numeric_value(value)
                self.variables[var_name] = numeric_value if numeric_value is not None else value

            elif cmd.name in ("add", "sub", "mul", "div"):
                if len(cmd.args) != 2:
                    print(f"L{cmd.line_number}: '{cmd.name}' requires 2 arguments.")
                    continue
                var_name, str_val = cmd.args
                if var_name not in self.variables:
                    print(f"L{cmd.line_number}: Variable '{var_name}' not found.")
                    continue

                val = self._get_numeric_value(str_val)
                if val is None:
                    print(f"L{cmd.line_number}: Second argument for '{cmd.name}' must be a number.")
                    continue

                if cmd.name == "add": self.variables[var_name] += val
                elif cmd.name == "sub": self.variables[var_name] -= val
                elif cmd.name == "mul": self.variables[var_name] *= val
                elif cmd.name == "div": self.variables[var_name] /= val

            elif cmd.name == "repeat":
                if not cmd.args: continue
                try:
                    count = int(cmd.args[0])
                except ValueError:
                    count = 1
                text = " ".join(cmd.args[1:])
                for _ in range(max(count, 0)):
                    print(text)

            elif cmd.name == "wait":
                if not cmd.args: continue
                try:
                    seconds = float(cmd.args[0])
                except ValueError:
                    seconds = 0.0
                time.sleep(max(seconds, 0.0))

            elif cmd.name == "window":
                title = " ".join(cmd.args) or "Aila"
                self.gui.create_window(title)
                self.window_created = True

            elif cmd.name == "label":
                self._require_window()
                self.gui.label(" ".join(cmd.args))

            elif cmd.name == "input":
                self._require_window()
                self.gui.input(" ".join(cmd.args))

            elif cmd.name == "button":
                self._require_window()
                text = " ".join(cmd.args) or "Button"
                self.gui.button(text, on_click=lambda: None)

            elif cmd.name == "show":
                self._require_window()
                self.gui.show(" ".join(cmd.args))

            elif cmd.name == "start":
                self._require_window()
                self.gui.start()
                break

            elif cmd.name == "close":
                self.gui.close()

            else:
                print(f"L{cmd.line_number}: Unknown command '{cmd.name}'")


