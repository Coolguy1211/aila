from typing import List
from .ast import AilaCommand

class Parser:
    """
    A simple parser for the Aila language.
    It tokenizes the source code on a line-by-line basis.
    """
    def __init__(self, source: str):
        self.source = source
        self.lines = source.splitlines()

    def parse(self) -> List[AilaCommand]:
        """
        Parses the source code and returns a list of Aila commands.
        """
        commands: List[AilaCommand] = []
        for i, raw_line in enumerate(self.lines):
            line = raw_line.strip()
            line_number = i + 1

            if not line or line.startswith("#"):
                continue

            parts = line.split()
            command_name = parts[0].lower()
            args = parts[1:]

            command = AilaCommand(
                name=command_name,
                args=args,
                line_number=line_number
            )
            commands.append(command)

        return commands
