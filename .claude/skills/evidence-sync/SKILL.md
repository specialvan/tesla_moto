---
name: evidence-sync
description: Synchronize V2 review evidence across claude-review docs, wiki pages, HTML snapshots, Codex review packages, and evidence manifests.
---

# Evidence Sync

Use this skill after creating or changing V2 engineering, review, simulation, prompt, or image-generation artifacts.

## Required destinations

For durable review knowledge, keep these in sync when applicable:

- `claude-review/docs/<date-or-version>/`
- `claude-docs/evidence_manifest.md`
- `wiki/`
- HTML snapshots or review pages under `claude-review/docs/**`
- `codex-review/docs/README.md` when responding to Codex feedback
- Scheme-level `engineering/v2/scheme-XX/README.md`
- Top-level `engineering/v2/README.md`

## Sync checklist

1. New review report has a durable Markdown file under `claude-review/docs`.
2. Any user-facing summary has matching wiki or HTML if the surrounding version already uses them.
3. `claude-docs/evidence_manifest.md` links the new evidence.
4. Codex return/rework items are linked from `codex-review/docs/README.md`.
5. Scheme READMEs reference new parameter, DVP, prompt, CAD, PCB, BOM/EDA, or simulation drafts.
6. Wording matches the current maturity posture: concept/parameter/proxy unless validated evidence exists.
7. Generated images, dry-run prompts, local configs, caches, and worktrees are not staged.

## Output format

Return:

- Added or updated evidence files
- Missing sync targets
- Wording/maturity mismatches
- Safe staging notes
