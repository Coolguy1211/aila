import time
from typing import List, Optional

from .gui import AilaGUI
from .ast import AilaCommand


class AilaInterpreter:
    """Simple line-oriented interpreter for the Aila language."""

    def __init__(self) -> None:
        self.gui = AilaGUI()
        self.window_created = False

    def parse(self, source: str) -> List[AilaCommand]:
        commands: List[AilaCommand] = []
        for i, raw_line in enumerate(source.splitlines()):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            name = parts[0].lower()
            args = parts[1:]
            commands.append(AilaCommand(name=name, args=args, line_number=i + 1))
        return commands

    def _require_window(self) -> None:
        if not self.window_created:
            # Create a default untitled window if user forgot `window`
            self.gui.create_window("Aila")
            self.window_created = True

    def execute(self, source: str) -> None:
        commands = self.parse(source)
        for cmd in commands:
            if cmd.name == "say":
                text = " ".join(cmd.args)
                print(text)
            elif cmd.name == "repeat":
                if not cmd.args:
                    continue
                try:
                    count = int(cmd.args[0])
                except ValueError:
                    count = 1
                text = " ".join(cmd.args[1:])
                for _ in range(max(count, 0)):
                    print(text)
            elif cmd.name == "wait":
                if not cmd.args:
                    continue
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
                default_text = " ".join(cmd.args)
                self.gui.input(default_text)
            elif cmd.name == "button":
                self._require_window()
                text = " ".join(cmd.args) or "Button"

                def no_op() -> None:
                    pass

                self.gui.button(text, on_click=no_op)
            elif cmd.name == "show":
                self._require_window()
                self.gui.show(" ".join(cmd.args))
            elif cmd.name == "start":
                self._require_window()
                # Start blocks; after it returns, break execution
                self.gui.start()
                break
            elif cmd.name == "close":
                self.gui.close()
            else:
                print(f"Unknown command: {cmd.name}")


