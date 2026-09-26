# dicelint

Dice notation (`2d6+3`, `d20`, `4d%`) shows up all over tabletop game data:
loot tables, encounter files, character sheets, homebrew rulebooks written
as plain text. It's easy to typo one of these strings in a way that a
downstream roller or simulator won't reject outright but will handle badly:
`0d6` silently rolls nothing, `d0` divides by zero in some implementations,
`20000d6` will make a naive simulator hang.

dicelint scans text for dice notation tokens and reports the ones that
look wrong, with a file name and line number, in the same style as most
compilers and linters.

## Install

No dependencies, nothing to build. Either run it in place:

```
python -m dicelint some_file.txt
```

or install it so the `dicelint` command is on your PATH:

```
pip install .
```

## Usage

```
$ cat loot_table.txt
common:    1d6
rare:      2d20+0d4
legendary: 20000d100
cursed:    3d0

$ dicelint loot_table.txt
loot_table.txt:3:12: DICE003 dice count 20000 is unreasonably large: '20000d100'
loot_table.txt:4:12: DICE001 die has zero sides: '3d0'
```

It also reads standard input when no files are given, which is what makes
it usable in a pipeline:

```
$ grep -h damage *.txt | dicelint
```

## Rules

| code    | meaning                                              |
|---------|-------------------------------------------------------|
| DICE001 | a die has zero sides (`d0`, `3d0`)                     |
| DICE002 | zero dice are rolled (`0d6`)                           |
| DICE003 | dice count is unreasonably large (default over 10,000) |
| DICE004 | side count is unreasonably large (default over 100,000)|
| DICE005 | a count, side, or keep/drop value has a leading zero (`01d6`) |
| DICE006 | a d1 is rolled, which always comes up 1                |
| DICE007 | a keep/drop modifier keeps or drops zero dice (`2d20kh0`) |
| DICE008 | a keep/drop count exceeds the dice rolled (`2d20kh3`)  |

## Library use

The checker is a generator, so it can be pointed at anything iterable line
by line - a file handle, `sys.stdin`, a socket wrapped in a text stream -
without ever holding the whole input in memory:

```python
from dicelint import lint_lines

with open("encounter.txt") as f:
    for finding in lint_lines(f, "encounter.txt"):
        print(finding.line, finding.code, finding.message)
```

`lint_lines` reads one line at a time from whatever iterable you give it
and yields findings as it goes, so a multi-gigabyte log of dice rolls is
fine to lint directly; nothing is buffered beyond the current line.

## Keep/drop modifiers

Rolls with a keep/drop modifier - `kh` (keep highest), `kl` (keep lowest),
`dh` (drop highest), `dl` (drop lowest) - followed by a count are
recognized as part of the same token, and the modifier's count is checked
against the number of dice actually rolled:

```
$ cat rolls.txt
advantage: 2d20kh1
oops:      4d6kh6

$ dicelint rolls.txt
rolls.txt:2:8: DICE008 keep/drop count 6 exceeds the 4 dice rolled: '4d6kh6'
```

## Known limitations

A single token is one roll of one die size; `2d6+1d4` is read as two
separate tokens rather than one combined roll, so a rule that reasons
about the roll as a whole (rather than each die independently) isn't
possible yet. See the project roadmap for what's planned next.
