# Parallel Agent Orchestration Template

## How to use this
Paste this prompt into your main Claude Opus session in VS Code, filling in the
[GOAL] section. Opus will decompose the work into parallel tasks, one per worker
agent. Each task output gets pasted into a separate terminal running `claude`.

**Important:** After Opus responds, save its full output to `.claude/current-sprint.md`
before starting any workers. This is your source of truth if you need to restart
a session or check progress.

---

## Orchestrator prompt

```
You are the orchestrator for a parallel coding pipeline.

Project context: Python 3.12 monorepo with FastAPI services and Dash/Plotly
interfaces, hexagonal architecture, SOLID principles, 80% test coverage minimum.
Full standards in CLAUDE.md.

Goal: [DESCRIBE WHAT YOU WANT TO BUILD]

Decompose this into parallel workstreams. For each workstream produce:

1. BRANCH NAME — follows feat/fix/chore/refactor convention
2. WORKER TASK — a precise, self-contained instruction for a Sonnet worker agent.
   The task MUST open with these two lines verbatim:
     "Start by running: git checkout -b <BRANCH_NAME>
      Do all work on this branch and commit your changes when done."
   Then include:
   - Exact files to create or modify
   - Interfaces/contracts this worker must respect
   - Dependencies on other workstreams (if any)
   - Acceptance criteria (how to know it is done)
   Every worker task MUST end with these steps verbatim:
     "Before opening a PR:
      1. Run: pytest --cov=src --cov-fail-under=80
         Do not open a PR if coverage is below 80%.
      2. Spawn a reviewer agent and ask it to review your changes against CLAUDE.md.
         Resolve all CRITICAL findings before opening the PR.
      3. Open the PR only after both steps pass."
3. HAIKU TASK — what the Haiku formatter should clean up after this worker
   finishes (docstrings, comment style, unused imports)

Rules:
- IMPORTANT: Do not write any code. Your only job is to produce the workstream
  plan. Worker agents will do all implementation.
- Each workstream must be independently executable with no runtime dependency
  on another workstream completing first
- If workstreams share an interface, define that interface first and include it
  in both worker tasks
- Maximum 4 parallel workstreams — more than that creates merge complexity
- Flag any workstream that MUST be sequential (e.g. migrations before services)

At the end, produce a SPRINT SUMMARY section with:
- Goal restated in one sentence
- List of all branches and what each delivers
- Merge order
- Any sequential dependencies to watch out for
```

---

## After Opus responds — save the sprint

Copy Opus's full response and save it — include your original goal at the top:

```bash
# In your repo root
mkdir -p .claude
# Paste Opus output into this file
code .claude/current-sprint.md
```

This file is your reference for the entire sprint. If you close the Opus session,
paste `current-sprint.md` back in and ask:

```
This is the sprint plan you produced earlier. Give me an overview of what 
has been implemented and what is still in progress.
```

---

## Worker agent startup command

For each workstream, open a new terminal and run:

```bash
agent worker <BRANCH_NAME>
```

Then paste the WORKER TASK from the orchestrator output.

## Haiku formatter startup command

After all workers finish, open a terminal and run:

```bash
agent format
```

Then paste the HAIKU TASK for each completed workstream one at a time.

---

## Merge order

1. Merge shared interfaces / domain models first
2. Merge services (infrastructure, API layers)
3. Merge web interfaces
4. Merge tests last — they may need to reference all of the above

Each branch goes through a PR — Claude review in VS Code + CI coverage gate
before merging.
