import shlex
from typing import List
from .ast import AilaCommand


class Parser:
    """
    A simple parser for the Aila language.
    It tokenizes the source code on a line-by-line basis.
    It uses shlex to handle quoted strings.
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

            try:
                parts = shlex.split(line)
            except ValueError as e:
                # Provide a more user-friendly error for unclosed quotes
                if "No closing quotation" in str(e):
                    print(f"Syntax Error at line {line_number}: Unclosed quote in line: '{line}'")
                else:
                    print(f"Syntax Error at line {line_number}: {e}")
                continue # Skip malformed lines

            if not parts:
                continue

            command_name = parts[0].lower()
            args = parts[1:]

            command = AilaCommand(
                name=command_name,
                args=args,
                line_number=line_number
            )
            commands.append(command)

        return commands
