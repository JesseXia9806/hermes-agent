# Glossary — Building Great Skills

The domain model for what makes a skill great. A skill exists to wrangle determinism out of a stochastic system; the root virtue is **Predictability**, and every term below is a lever on it.

The terms are grouped by axis: **Invocation** (how a skill is reached), **Information Hierarchy** (how its content is arranged), **Steering** (how the agent's runtime behaviour is shaped), and **Pruning** (how it is kept lean).

## Predictability

The degree to which a skill makes the agent behave the same _way_ on every run — the same process, not the same output. The root virtue every other term serves.

## Invocation

### Model-Invoked

A skill that keeps its **description** field, so the agent can see it and fire it autonomously — and the human can still type its name. Pays a permanent **context load** on every turn. Reachable by other skills.

### User-Invoked

A skill with its **description** stripped — invisible to the agent and reachable only by the human typing its name. Trades agent-discoverability for zero **context load**.

### Description

The skill's machine-readable trigger, and the one **context pointer** a **model-invoked** skill keeps loaded at all times.

### Context Pointer

A reference held in the agent's context that names some out-of-context material and encodes the condition for reaching it.

### Context Load

The cost a **model-invoked** skill imposes on the agent's context window — its **description**, always loaded.

### Cognitive Load

The cost a **user-invoked** skill imposes on the human — what they must hold in their head: which skills exist and when to reach for each.

### Router Skill

A **user-invoked** skill whose job is to point at your other user-invoked skills — naming each and when to reach for it.

### Granularity

How finely you divide skills. Finer division spends one of the two loads: more **model-invoked** skills spend **context load**; more **user-invoked** skills spend **cognitive load**.

## Information Hierarchy

### Information Hierarchy

A skill's content ranked by how immediately the agent needs it — a single ladder:
- **Steps** — in-file, primary
- **Reference**, in-file — secondary
- **Reference**, disclosed — behind a **context pointer**

### Steps

The ordered actions the agent performs — the primary tier of content. Every step ends on a **completion criterion**.

### Reference

Material the agent refers to on demand — definitions, facts, parameters, examples.

### External Reference

**Reference** that lives outside the skill system that any skill can point at.

### Progressive Disclosure

Moving **reference** down the ladder — out of SKILL.md and behind a **context pointer** — so the top stays legible.

### Co-location

Keeping the material an agent needs at once in one place.

### Sprawl

_Failure mode._ A skill that is simply too long. The cure is the **information hierarchy**.

## Steering

### Branch

A distinct way a skill can be invoked — a case the skill handles.

### Leading Word

A compact concept already living in the model's pretraining, that the agent thinks with while running the skill.

### Completion Criterion

The condition that tells the agent a unit of work is done.

### Legwork

The work an agent does behind the scenes within a single step.

### Post-Completion Steps

The **steps** that follow the current step. Visible, they pull the agent forward into **premature completion**.

### Premature Completion

_Failure mode._ Ending the current step before it is genuinely done.

### Negation

_Failure mode._ Steering by prohibition — telling the agent what _not_ to do — which drags the forbidden behaviour into context.

## Pruning

### Single Source of Truth

The desired state where each meaning lives in exactly one authoritative place.

### Duplication

_Failure mode._ The same meaning given more than one **single source of truth**.

### Relevance

Whether a line still bears on what the skill does.

### Sediment

_Failure mode._ Layers of old content that settle in a skill and are never cleared.

### No-Op

_Failure mode._ An instruction that changes nothing because the model already does it by default.
