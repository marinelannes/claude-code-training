"""Reset the repository to the start of a lab.

Usage (Windows, macOS, Linux): uv run python scripts/reset.py

- discards changes to tracked files,
- switches to the main branch,
- deletes untracked files in the project folders (src, tests, scripts, notebooks, data, out, docs).

It never touches CLAUDE.md, .claude/ or ignored files, so your Claude Code setup survives.
Commit or branch anything you want to keep before running it.
"""

from __future__ import annotations

import subprocess
import sys

CLEAN_PATHS = ["src", "tests", "scripts", "notebooks", "data", "out", "docs"]


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout


def main() -> None:
    git("restore", "--staged", "--worktree", "--", ".")
    if git("branch", "--show-current").strip() != "main":
        git("switch", "main")
    removed = git("clean", "-fd", "--", *CLEAN_PATHS)
    print(removed.strip() or "No untracked file to remove.")
    print("Done: on main, project files reset.")


if __name__ == "__main__":
    main()
