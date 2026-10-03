---
name: teach
description: "Teach the user a new skill or concept, within the current workspace. Creates a stateful teaching environment with lessons, learning records, and resources."
metadata:
  hermes:
    tags: [productivity, learning, teaching, education]
---

The user has asked you to teach them something. This is a stateful request — they intend to learn the topic over multiple sessions.

## Teaching Workspace

Treat the current directory as a teaching workspace. The state of their learning is captured in this directory in several files:

- `MISSION.md`: A document capturing the _reason_ the user is interested in the topic. Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./reference/*.html`: A directory of reference materials — cheat sheets, reference algorithms, syntax, glossaries.
- `RESOURCES.md`: A list of resources. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./learning-records/*.md`: A directory of learning records (like ADRs for learning). Use the format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `./lessons/*.html`: A directory of lessons — self-contained HTML output that teaches one tightly-scoped thing.
- `./assets/*`: Reusable components shared across lessons.
- `NOTES.md`: A scratchpad for user preferences.

## Philosophy

To learn at a deep level, the user needs three things:
- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons
- **Wisdom**, from interacting with other learners and practitioners

### Fluency vs Storage Strength

- **Fluency strength**: in-the-moment retrieval
- **Storage strength**: long-term retention — the real goal

Design lessons which build long-term retention by desirable difficulty:
- Retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing related topics)

## Lessons

Each lesson is one self-contained HTML file, saved to `./lessons/` titled `0001-<dash-case-name>.html`. Lessons should be **beautiful** (clean typography), short, and completable quickly. Each lesson should give the user a single tangible win tied to the mission.

Each lesson should link via HTML anchors to other lessons, reference documents, and a recommended primary source.

## The Mission

Every lesson ties into the mission — the reason the user is learning. If the mission is unclear, interview the user first. Missions may change as skills develop.

## Zone Of Proximal Development

Each lesson should challenge the user 'just enough'. Determine the zone by reading learning records and the mission.

## Knowledge & Skills

Knowledge should be gathered from trusted resources first. Skills are taught through interactive feedback loops — quizzes, guided steps, real-world exercises. For skill acquisition, difficulty is the tool.

## Reference Documents

Create reference documents alongside lessons — compressed essence for quick reference. Glossaries are essential once vocabulary builds up.

## Acquiring Wisdom

Default: attempt to answer, then delegate to a **community** (forum, subreddit, class, interest group). Respect if the user opts out of communities.
