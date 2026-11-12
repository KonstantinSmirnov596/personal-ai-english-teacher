"""Reads the window's string files (web/i18n/<code>.js) without a JavaScript engine.

The files are one ``export default { ... }`` object literal whose values are string literals,
arrays of string literals, nested objects or arrow functions. This parser understands exactly
that subset and returns a flat map: key path -> ("str", text) | ("list", [texts]) |
("fn", parameter count). Anything else is a test failure, which keeps the files simple.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_IDENT = re.compile(r"[A-Za-z_$][\w$]*")


class ParseError(ValueError):
    pass


class _Parser:
    def __init__(self, text: str) -> None:
        self.s = text
        self.i = 0

    def ws(self) -> None:
        while self.i < len(self.s):
            if self.s[self.i].isspace():
                self.i += 1
            elif self.s.startswith("//", self.i):
                self.i = self.s.find("\n", self.i) if "\n" in self.s[self.i :] else len(self.s)
            else:
                return

    def expect(self, token: str) -> None:
        self.ws()
        if not self.s.startswith(token, self.i):
            raise ParseError(f"expected {token!r} at {self.i}: {self.s[self.i : self.i + 40]!r}")
        self.i += len(token)

    def string(self) -> str:
        quote = self.s[self.i]
        if quote not in "'\"":
            raise ParseError(f"expected a string at {self.i}")
        self.i += 1
        out = []
        while self.s[self.i] != quote:
            ch = self.s[self.i]
            if ch == "\\":
                nxt = self.s[self.i + 1]
                out.append({"n": "\n", "t": "\t"}.get(nxt, nxt))
                self.i += 2
                continue
            out.append(ch)
            self.i += 1
        self.i += 1
        return "".join(out)

    def skip_balanced_expression(self) -> None:
        """Skip an arrow-function body up to the ',' or '}' that ends the property."""
        depth = 0
        while self.i < len(self.s):
            ch = self.s[self.i]
            if ch in "'\"":
                self.string()
                continue
            if ch == "`":
                self.i += 1
                while self.s[self.i] != "`":
                    if self.s.startswith("${", self.i):
                        self.i += 2
                        inner = 1
                        while inner:
                            c = self.s[self.i]
                            if c == "{":
                                inner += 1
                            elif c == "}":
                                inner -= 1
                            elif c in "'\"":
                                self.string()
                                continue
                            self.i += 1
                        continue
                    self.i += 2 if self.s[self.i] == "\\" else 1
                self.i += 1
                continue
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                if depth == 0:
                    return
                depth -= 1
            elif ch == "," and depth == 0:
                return
            self.i += 1

    def value(self) -> Any:
        self.ws()
        ch = self.s[self.i]
        if ch in "'\"":
            return ("str", self.string())
        if ch == "{":
            return ("obj", self.obj())
        if ch == "[":
            self.i += 1
            items = []
            while True:
                self.ws()
                if self.s[self.i] == "]":
                    self.i += 1
                    return ("list", items)
                items.append(self.string())
                self.ws()
                if self.s[self.i] == ",":
                    self.i += 1
        if ch == "(":
            close = self.s.index(")", self.i)
            params = [p for p in self.s[self.i + 1 : close].split(",") if p.strip()]
            self.i = close + 1
            self.expect("=>")
            self.skip_balanced_expression()
            return ("fn", len(params))
        raise ParseError(f"unsupported value at {self.i}: {self.s[self.i : self.i + 40]!r}")

    def obj(self) -> dict[str, Any]:
        self.expect("{")
        out: dict[str, Any] = {}
        while True:
            self.ws()
            if self.s[self.i] == "}":
                self.i += 1
                return out
            m = _IDENT.match(self.s, self.i)
            if m:
                key = m.group(0)
                self.i = m.end()
            else:
                key = self.string()
            self.expect(":")
            out[key] = self.value()
            self.ws()
            if self.s[self.i] == ",":
                self.i += 1


def parse_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    start = text.index("export default")
    p = _Parser(text)
    p.i = start + len("export default")
    return p.obj()


def flatten(obj: dict[str, Any], prefix: str = "") -> dict[str, tuple[str, Any]]:
    flat: dict[str, tuple[str, Any]] = {}
    for key, (kind, val) in obj.items():
        path = f"{prefix}{key}"
        if kind == "obj":
            flat.update(flatten(val, path + "."))
        else:
            flat[path] = (kind, val)
    return flat
