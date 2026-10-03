# Learning Record Format

Learning records live in `./learning-records/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc.

They are the teaching equivalent of ADRs: they capture non-obvious lessons, key insights, and stated prior knowledge that will steer future sessions.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it matters for future sessions.}
```

## Optional sections

- **Status** frontmatter (`active | superseded by LR-NNNN`)
- **Evidence** — how the user demonstrated the understanding
- **Implications** — what this unlocks or rules out

## When to write

1. The user demonstrated genuine understanding of something non-trivial
2. The user disclosed prior knowledge
3. A misconception was corrected
4. The mission shifted in response to learning

## What does _not_ qualify

- Material that was merely covered
- Anything already captured in a glossary
- Session-by-session activity logs

## Supersession

When a later record contradicts an earlier one, mark the old record `Status: superseded by LR-NNNN` rather than deleting it.
