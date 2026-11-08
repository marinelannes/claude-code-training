# Lab 3 · Refactor messy code (50 min)

**Goal:** turn messy, working code into a clean, tested package without changing its
behaviour.

**Starting point:** `main` plus your Lab 2 harness.

- Developers: `scripts/monthly_report.py`.
- Data scientists: you may take `notebooks/monthly_report.ipynb` instead. Close it in
  Jupyter before Claude edits it.

## Steps

1. **Pin the behaviour.** Run the report and save its output as the golden file:
   ```bash
   uv run python scripts/monthly_report.py
   mkdir -p tests/golden
   cp out/report_2026_01.csv tests/golden/report_2026_01.csv
   ```
   With Claude, write a characterization test in `tests/unit/` that runs the report and
   compares its CSV output with the golden file, byte for byte.
2. **Commit** the test and the golden file now. This must happen before you create the
   worktree, otherwise the worktree does not contain them.
3. **Plan.** In plan mode, ask for a target package structure (for example
   `src/orders/reporting/` with loading, computation and formatting). Review the plan and
   amend it before accepting.
4. **Execute.** Start a session in a new worktree (`claude --worktree`) and give it a `/goal`:
   the characterization test passes and `python scripts/monthly_report.py` still works.
5. **Verify.** Run the old and the new entry points, compare the outputs, read the diff.

## Done when

The golden test is green and the old entry point still works.

## Stretch goal

Make the notebook a thin client of the new package: it only imports and calls functions.
