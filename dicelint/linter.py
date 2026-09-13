"""Rule checks and the line-by-line driver.

lint_lines() takes any iterable of lines - a real file object, sys.stdin,
a list, whatever - and yields Finding objects as it goes. It never
collects the input into a list or a big string, so a caller can point it
at a multi-gigabyte file and it will only ever hold one line in memory
at a time.
"""

import re
from typing import Iterable, Iterator, Optional

from .notation import TOKEN_RE, Finding

# Past these, a roll is almost certainly a typo rather than something a
# game actually wants simulated (a 20d20 encounter table is plausible,
# a 20000d20 one is not).
MAX_REASONABLE_COUNT = 10_000
MAX_REASONABLE_SIDES = 100_000


def _check_token(match: re.Match, lineno: int) -> Optional[Finding]:
    count_str = match.group("count")
    sides_str = match.group("sides")
    text = match.group(0)
    column = match.start() + 1

    if count_str and count_str != "0" and count_str.startswith("0"):
        return Finding(
            lineno, column, "DICE005",
            f"dice count has a leading zero: {text!r}", text,
        )

    count = int(count_str) if count_str else 1

    if count == 0:
        return Finding(
            lineno, column, "DICE002",
            f"zero dice rolled: {text!r}", text,
        )

    if count > MAX_REASONABLE_COUNT:
        return Finding(
            lineno, column, "DICE003",
            f"dice count {count} is unreasonably large: {text!r}", text,
        )

    if sides_str == "%":
        return None

    if sides_str != "0" and sides_str.startswith("0"):
        return Finding(
            lineno, column, "DICE005",
            f"side count has a leading zero: {text!r}", text,
        )

    sides = int(sides_str)

    if sides == 0:
        return Finding(
            lineno, column, "DICE001",
            f"die has zero sides: {text!r}", text,
        )

    if sides == 1:
        return Finding(
            lineno, column, "DICE006",
            f"a d1 always rolls 1, the die is pointless: {text!r}", text,
        )

    if sides > MAX_REASONABLE_SIDES:
        return Finding(
            lineno, column, "DICE004",
            f"side count {sides} is unreasonably large: {text!r}", text,
        )

    return None


def lint_lines(lines: Iterable[str], filename: str = "<stdin>") -> Iterator[Finding]:
    for lineno, line in enumerate(lines, start=1):
        for match in TOKEN_RE.finditer(line):
            finding = _check_token(match, lineno)
            if finding is not None:
                yield finding
