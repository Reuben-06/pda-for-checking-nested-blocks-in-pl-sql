#!/usr/bin/env python3
"""Check balanced PL/SQL block delimiters using a simplified stack model."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

TOKEN_RE = re.compile(
    r"(?P<comment_line>--[^\n]*)|(?P<comment_block>/\*.*?\*/)|"
    r"(?P<string>'(?:''|[^'])*')|(?P<quoted_identifier>\"(?:\"\"|[^\"])*\")|"
    r"(?P<word>[A-Za-z][A-Za-z0-9_$#]*)|(?P<other>.)",
    re.DOTALL,
)

OPENERS = {"BEGIN": "BEGIN", "IF": "IF", "LOOP": "LOOP", "CASE": "CASE"}
CLOSERS = {"IF": "IF", "LOOP": "LOOP", "CASE": "CASE"}

@dataclass
class Token:
    value: str
    line: int
    column: int

@dataclass
class OpenBlock:
    kind: str
    token: Token


def tokenize(source: str) -> list[Token]:
    """Return significant words only; ignore comments, strings, and identifiers."""
    result: list[Token] = []
    for match in TOKEN_RE.finditer(source):
        if match.lastgroup != "word":
            continue
        before = source[:match.start()]
        line = before.count("\n") + 1
        last_newline = before.rfind("\n")
        column = match.start() - last_newline
        result.append(Token(match.group().upper(), line, column))
    return result


def check(source: str, show_stack: bool = False) -> list[str]:
    """Return errors and optionally print each stack transition."""
    stack: list[OpenBlock] = []
    errors: list[str] = []
    tokens = tokenize(source)
    if show_stack:
        print("\nPDA STACK TRACE (top is on the right)")
        print("Initial stack: []")
    i = 0
    while i < len(tokens):
        token = tokens[i]
        word = token.value
        if word == "END":
            next_word = tokens[i + 1].value if i + 1 < len(tokens) else None
            if next_word in CLOSERS:
                expected = CLOSERS[next_word]
                close_label = f"END {next_word}"
                i += 1
            else:
                expected = "BEGIN"
                close_label = "END"
            if not stack:
                errors.append(f"Line {token.line}, column {token.column}: {close_label} has no matching opener.")
                if show_stack:
                    print(f"Line {token.line}: read {close_label:<9} -> ERROR (stack is empty)")
            elif stack[-1].kind == expected:
                stack.pop()
                if show_stack:
                    print(f"Line {token.line}: read {close_label:<9} -> pop {expected:<5} stack={stack_view(stack)}")
            else:
                opener = stack[-1]
                errors.append(
                    f"Line {token.line}, column {token.column}: {close_label} cannot close {opener.kind} "
                    f"opened at line {opener.token.line}; expected its matching END."
                )
                if show_stack:
                    print(f"Line {token.line}: read {close_label:<9} -> MISMATCH (top is {opener.kind}) stack={stack_view(stack)}")
                # Keep the stack intact so the final report can show unclosed blocks too.
        elif word in OPENERS:
            stack.append(OpenBlock(OPENERS[word], token))
            if show_stack:
                print(f"Line {token.line}: read {word:<9} -> push {word:<5} stack={stack_view(stack)}")
        i += 1
    for block in reversed(stack):
        errors.append(f"Line {block.token.line}, column {block.token.column}: {block.kind} block is not closed.")
    return errors


def stack_view(stack: list[OpenBlock]) -> list[str]:
    """Format stack contents from bottom to top for the demo trace."""
    return [block.kind for block in stack]


def main() -> int:
    parser = argparse.ArgumentParser(description="Check nested PL/SQL blocks (simplified educational model).")
    parser.add_argument("file", nargs="?", help="PL/SQL source file; omit to read from standard input")
    parser.add_argument("--trace", action="store_true", help="show PDA stack transitions while checking")
    args = parser.parse_args()
    try:
        source = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    except OSError as exc:
        print(f"Could not read input: {exc}", file=sys.stderr)
        return 2
    errors = check(source, show_stack=args.trace)
    if errors:
        print("INVALID: unbalanced blocks found")
        for error in errors:
            print(f"- {error}")
        return 1
    print("VALID: all recognized blocks are properly nested")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
