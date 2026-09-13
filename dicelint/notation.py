"""Recognizing dice notation tokens inside arbitrary text.

Dice notation shows up embedded in loot tables, encounter files, character
sheets, etc, mixed in with prose and other numbers. The regex below is
deliberately conservative: it only matches a run of digits directly attached
to a "d", and refuses to match if that run is itself glued to other letters
or digits (so "added6" or "1d6x" are left alone). Notation with keep/drop
modifiers (4d6kh3) is not recognized yet - see the README roadmap.
"""

import re
from dataclasses import dataclass

TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])(?P<count>\d*)d(?P<sides>\d+|%)(?![A-Za-z])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    line: int
    column: int
    code: str
    message: str
    text: str
