# Labs

Five hands-on labs on this repository, plus bonus exercises. Each lab file gives the goal,
the time box, the starting point, the steps and the "done when" criterion.

| Lab | Topic | Time |
|-----|-------|------|
| [Lab 1](lab1.md) | Models & effort | 35 min |
| [Lab 2](lab2.md) | Build the harness | 60 min |
| [Lab 3](lab3.md) | Refactor messy code | 50 min |
| [Lab 4](lab4.md) | A loop with a judge | 60 min |
| [Lab 5](lab5.md) | Document a module | 25 min |
| [Bonus](bonus.md) | Parallel work and subagents | open |

## Before you start

```bash
uv sync
uv run pytest
```

Both commands must succeed. On Windows, use **Git Bash** for the commands of these labs.

## Reset to the start of a lab

Commit or branch anything you want to keep, then run:

```bash
uv run python scripts/reset.py
```

It discards your changes to tracked files, switches to `main` and deletes untracked files in
the project folders. It keeps `CLAUDE.md`, `.claude/` and ignored files, so your Claude Code
setup from Lab 2 survives. The same thing with raw git commands, one per line:

```bash
git restore --staged --worktree -- .
git switch main
git clean -fd -- src tests scripts notebooks data out docs
```

## Solutions

There are solutions for every lab. The trainer will share them at the end of the training.
