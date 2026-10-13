---
name: frugal-fable
description: Plan bounded model delegation with explicit ownership, evidence gates and honest cost limits; use only authorized available agents and runtime capabilities.
metadata:
  version: "2.0.0-review.1"
  edition: "Local review edition; not an upstream release"
---


    # Frugal delegation
    Keep ambiguous/high-impact decisions, integration and final evidence review with the
    orchestrator. Delegate only when allowed by user/host policy and independently useful.
    One small or coupled task stays local. Capability labels are not current model IDs.
    Discover supported tools/models/effort at runtime; do not change the user's model
    preference or assume another subscription has free or generous quota.

    ## Plan
    Load references/routing-cheatsheet.md. Name objective, owner files, dependencies,
    constraints, output path, required checks and stopping conditions for each slice.
    Disjoint writes or isolated worktrees; tell workers they share the workspace and must
    preserve others' edits. Do not overwrite source from a stale patch.
    Use a unique run ID under an agreed scratch root; validate returned paths remain inside
    it. Keep summaries small, full evidence on disk. Scratch files are private and must
    not be committed/uploaded casually; no automatic gitignore/config edits.

    ## Costs and execution
    Load references/budget-and-evidence.md before fan-out. Separate measured total/input/
    output/cached/reasoning tokens, estimated cost and account quota. Output-only metering
    cannot enforce total token spend. An input/output multiplier is only an estimate.
    scripts/scheduler.mjs supplies reservation-before-launch, bounded concurrency/call
    count, fail-closed accounting and evidence gates. It needs an explicit adapter;
    it neither calls providers nor promises provider-level budget enforcement.
    Strict spend limits require a trusted adapter to enforce each inclusive upper bound,
    report actual total usage including nested calls/retries, and stop/cancel at limits.
    If that capability is absent, run serial limited work under an advisory estimate,
    disclose uncertainty, or decline a strict-budget run. Never label it a hard cap.
    Include orchestration, retrieval, verification, retries and final synthesis in planning.
    Conflicting cost modes need a clear choice only when conflict is established; don't
    claim a toggle exists or stop based on an assumed mode.

    ## Integrate
    Missing verification, failed checks, stopped workers or unavailable evidence are not
    accepted work. High-stakes verification needs the same capability floor as construction.
    Reopen cited evidence and relevant diff. Research votes may be correlated: two replies
    are not two independent sources. Agreement is a lead, split votes are disputed, no
    usable evidence is unknown; don't rename surviving claims "confirmed".
    Continue essential work within agreed scope/reserve; seek scope changes only when needed.
    Report completed/skipped/failed slices, evidence, actual or estimated costs and unresolved
    issues. Local mechanics tests cannot establish model quality or economic savings.
    For external CLI delegation read references/codex-delegation.md.
