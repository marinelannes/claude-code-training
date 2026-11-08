# Reference cases

This folder will hold the reference cases for pricing, written by the team by hand from
`specs/pricing.md`: one test per business rule, each with the hand computation in a comment.
They are the judge for any change to `src/orders/pricing.py`, and nobody edits them to make
the code pass. Verification command: `uv run pytest tests/reference -q`
