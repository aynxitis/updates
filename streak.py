#!/usr/bin/env python3
"""Append an update to README.md, then commit and push it.

Run it as often as you like. Each run is update N, N+1, N+2...
Operates on the directory the script lives in.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent
README = REPO / "README.md"
COUNTER = REPO / ".count"
MARKER = "<!-- log -->"


def git(*args: str) -> str:
    """Run a git command in the repo. Raises on non-zero exit."""
    result = subprocess.run(
        ["git", *args],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def main() -> int:
    if not README.exists():
        print("README.md not found. Create it first, with a line containing:", MARKER)
        return 1

    text = README.read_text(encoding="utf-8")

    if MARKER not in text:
        print(f"README.md needs a line containing {MARKER} to mark where entries go.")
        return 1

    n = int(COUNTER.read_text().strip()) if COUNTER.exists() else 1
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    entry = f"| {n} | {stamp} |"
    README.write_text(text.replace(MARKER, MARKER + "\n" + entry), encoding="utf-8")
    COUNTER.write_text(str(n + 1) + "\n", encoding="utf-8")

    try:
        git("add", "README.md", ".count")
        git("commit", "-m", f"update #{n}")
        git("push")
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        print("Local files were updated. Fix the issue and run: git push", file=sys.stderr)
        return 1

    print(f"Pushed update #{n}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
