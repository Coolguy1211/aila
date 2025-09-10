from dataclasses import dataclass
from typing import List

@dataclass
class AilaCommand:
    """Represents a single command in an Aila program."""
    name: str
    args: List[str]
    line_number: int
