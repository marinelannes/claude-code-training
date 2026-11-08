# Bonus · Parallel work and subagents

## (a) Two features in parallel

Run two Claude sessions at the same time, each in its own worktree, on disjoint files:

1. **Italy.** Add Italy (`IT`, VAT 22%) to the pricing module and to the importer, with
   tests.
2. **JSON output.** Add a `--format json` option to `python -m orders price`, with a test.

Use `claude --worktree` in two terminals. On macOS or Linux (or WSL on Windows), you can run
each session in its own tmux session (`tmux new -s italy`, detach with `Ctrl-b` then `d`).
The desktop app is another option. Check each worktree's tests, then merge both branches.

## (b) A test-writer subagent

Write `.claude/agents/test-writer.md`: a subagent that only writes tests, restricted to the
`tests/` folder, with a small model. Ask Claude to delegate the tests of your Italy feature
to it, and review what comes back.
