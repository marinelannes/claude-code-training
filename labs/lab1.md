# Lab 1 · Models & effort (35 min)

**Goal:** implement the same feature with different models and effort levels, and choose
your default setting from evidence.

**Starting point:** `main`. The importer `src/orders/importer.py` is an empty skeleton.
Its rules are in `specs/importer.md`, and the acceptance tests in `tests/acceptance/` define
the expected behaviour. They all fail for now:

```bash
uv run pytest tests/acceptance -q
```

## Steps

1. Write your prompt in a file outside the project folders, for example `prompts/lab1.md`,
   so that every run gets exactly the same prompt. Point Claude at the spec with `@`.
2. **Run 1: Haiku.** Start `claude`, select the model with `/model`, check `/usage`, paste
   the prompt. Note the wall-clock time, the tokens used, and `/usage` at the end.
3. Check the result and save it on a branch:
   ```bash
   uv run pytest tests/acceptance -q
   git diff --stat main
   git switch -c lab1-haiku
   git add -A
   git commit -m "Lab 1: Haiku run"
   uv run python scripts/reset.py
   ```
4. **Run 2: Opus at high effort** (`/model`, then `/effort high`), in a new session
   (`/clear`). Repeat step 3 with the branch `lab1-opus-high`.
5. **Run 3 (if time allows): Sonnet at medium effort.** Branch `lab1-sonnet-medium`.
6. Compare the runs in a small table: passing acceptance tests, time, tokens and usage,
   diff size, and how readable the code is.

## Done when

You can say which setting you would use by default for this kind of task, and why.

## Stretch goal

Run `uv run python -m orders import data/orders_2026_02_raw.csv --month 2026-02` on your best
branch and check that the counts match the acceptance tests.
