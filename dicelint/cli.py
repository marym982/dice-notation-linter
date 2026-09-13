import argparse
import sys

from .linter import lint_lines


def _lint_stream(stream, name: str) -> int:
    exit_code = 0
    for finding in lint_lines(stream, name):
        print(f"{name}:{finding.line}:{finding.column}: {finding.code} {finding.message}")
        exit_code = 1
    return exit_code


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="dicelint",
        description="Check dice notation (2d6+3, d20, 4d%%) for common mistakes.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="files to check; reads standard input if omitted",
    )
    args = parser.parse_args(argv)

    if not args.paths:
        return _lint_stream(sys.stdin, "<stdin>")

    exit_code = 0
    for path in args.paths:
        with open(path, "r", encoding="utf-8") as handle:
            exit_code |= _lint_stream(handle, path)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
