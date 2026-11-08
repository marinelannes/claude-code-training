# Lab 5 · Document a module (25 min)

**Goal:** produce documentation you can trust: docstrings, a README and a shareable summary.

**Starting point:** your Lab 4 result (or `main` plus your Lab 2 harness).

## Steps

1. Run your docstring skill from Lab 2 on `src/orders/pricing.py`.
2. Ask Claude to rewrite `README.md`: purpose, install, usage, project layout.
3. **Claim check.** Ask Claude to list every factual claim in the README (commands, options,
   behaviours, rules) and to check each one against the code and the specs, quoting the
   evidence. Fix every claim that is false.
4. Produce a one-page summary of the pricing rules for the sales team: publish it as an
   artifact if your plan allows it, otherwise write `docs/pricing_summary.md`.

## Done when

No claim in the README is false.

## Stretch goal

Add a test that runs every command written in the README, so it cannot drift again.
