"""Recognizing dice notation tokens inside arbitrary text.

Dice notation shows up embedded in loot tables, encounter files, character
sheets, etc, mixed in with prose and other numbers. The regex below is
deliberately conservative: it only matches a run of digits directly attached
to a "d", and refuses to match if that run is itself glued to other letters
or digits (so "added6" or "1d6x" are left alone).

A roll can also carry a keep/drop modifier - kh (keep highest), kl (keep
lowest), dh (drop highest), dl (drop lowest) - followed by a count, as in
"4d6kh3" or "2d20kl1". The modifier is folded into the same token so it
stays attached to the roll it belongs to and its count can be checked
against the number of dice actually rolled.
"""

import re
from dataclasses import dataclass

TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9])(?P<count>\d*)d(?P<sides>\d+|%)"
    r"(?:(?P<modtype>kh|kl|dh|dl)(?P<modcount>\d+))?"
    r"(?![A-Za-z0-9])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Finding:
    line: int
    column: int
    code: str
    message: str
    text: str
