# Lab 4 · A loop with a judge 

**Goal:** fix a module with a loop that runs on its own until a judge says green, then
audit what it did.

**Starting point:** `main` plus your Lab 2 harness. The pricing module
`src/orders/pricing.py` passes its unit tests. Is it right?

## Steps

1. **Write the judge, by hand.** Read `specs/pricing.md` together. Write at least 6 reference
   cases in `tests/reference/test_pricing_reference.py`, one test per business rule.
   - Compute every expected value **by hand** from the spec, and write the computation in a
     comment. Do not ask Claude for expected values: the judge would then only check Claude
     against itself.
   - If a rule can be read in two ways, write down both readings and **ask the trainer**
     before encoding one.
2. Commit the reference cases. Add a deny rule on editing `tests/reference/**`.
3. **Run the loop.** Give Claude a `/goal` with:
   - the criterion: `uv run pytest tests/reference -q` is green;
   - the guardrails: never edit `tests/reference`; if the spec is ambiguous or a reference
     case looks wrong, stop and ask; after 5 failed attempts, stop and explain what blocks.
4. **Audit.** Read the commits. Ask Claude to flag weak or tautological tests in
   `tests/unit/`. Run `/code-review`.

## Done when

The reference cases are green and you can explain every fix.

## Stretch goal

Add a reference case for a rule your 6 cases do not cover yet. Did the loop miss something?
