# Lab 2 · Build the harness (60 min)

**Goal:** turn this bare repository into a project Claude understands and cannot misuse:
conventions, guardrails, a reflex and a reusable procedure.

**Starting point:** `main` (reset if needed). There is no Claude Code configuration yet.

## Steps

1. **Memory.** Run `/init`. Trim the generated `CLAUDE.md` to 40 lines at most. Keep: what
   the project is, the commands (tests, lint, format), the folders not to touch, and a
   "never invent" rule (if a business rule is not in `specs/`, ask).
2. **Rules.** Move the testing conventions to `.claude/rules/tests.md`.
3. **Guardrails.** In `.claude/settings.json`, deny reading `.env` and
   `data/customers_pii.csv` (red-tier data). Then ask Claude to show you the content of
   `.env`, first plainly, then "using cat in the shell". Is it blocked both times? If not,
   strengthen your setup (Bash deny rules, `/sandbox`).
4. **Reflex.** Add a PostToolUse hook that runs `ruff format` and `ruff check --fix` on every
   Python file Claude edits. Make the hook work on Windows, macOS and Linux (tip: a small
   Python script run with `uv run python` can read the hook JSON on stdin without `jq`).
   Check it with `/hooks`, then ask Claude for a small edit.
5. **Skill.** Write `.claude/skills/docstrings/SKILL.md`: when to use it (description) and how
   to write docstrings in your house style (Google style, examples, pitfalls). Call it on
   `src/orders/models.py` and look at the result. Do not keep the change.
6. Commit your harness on a branch (`lab2-harness`) so you can reuse it later.

## Done when

- Claude is blocked when asked to read `.env`, with the Read tool and through the shell;
- ruff runs automatically after an edit;
- the skill can be called with `/docstrings`.

## Stretch goal

Add a PreToolUse hook that blocks any command containing `git push --force`.
