---
name: prd-creator
description: Turn product context into a traceable, right-sized requirements document; discover material unknowns and validate choices without forcing a lengthy interview.
metadata:
  version: "2.0.0-review.1"
  edition: "Local review edition; not an upstream release"
---


    # PRD creator
    Read existing context first and respect the requested depth, output format and stack.
    Default to one useful PRD, not a fixed-length interview or predetermined architecture.
    Local desktop/CLI with a filesystem: save at the agreed path. Chat-only: downloadable
    artifact. HTML requests take precedence over the historical Markdown default.
    Use the host's available question tool, or concise conversation; never assume a tool
    exists or a particular mode allows it.

    ## Discover in proportion to risk
    Load references/questioning-patterns.md. Cover flows, audience, platform, UX/accessibility,
    data, auth/roles/privacy, integrations, scale, risks, budget/timeline/builder and existing
    materials using known context, questions, explicit assumptions or justified N/A.
    Ask questions whose answers would change a decision; no minimum question count.
    Prioritize irreversible choices, money, privacy, ambiguous permission and loss of data.
    Explain options at the user's level. Do not infer expertise solely from vocabulary.
    Explicit user constraints need no repeat confirmation.

    ## Decide and validate
    Compare configure/buy/build against the user's must-have and existing subscriptions.
    Separate confirmed constraints, researched facts, recommendations and assumptions.
    Browse official pricing/docs for changing claims; record date, region, currency,
    allowance, overage, data export and exit cost. If inaccessible mark cost unknown.
    Recommend minimal viable architecture; leave replaceable implementation details open.
    Load references/tool-integration.md for research boundaries.
    For AI products consider inference/retrieval costs, output evaluation, prompt injection,
    data retention, rights, fallback and authorized tool actions as applicable, not boilerplate.

    ## Write and refine
    Load references/prd-template.md and output-examples.md. Each requirement has a stable ID,
    source, priority, measurable acceptance, failure/edge behavior and verification method.
    Distinguish proposed acceptance criteria from user-confirmed requirements.
    Include ownership, retention/deletion/export, restore behavior, operational burden,
    third-party outages and a testable launch/rollback condition where relevant.
    Mark unresolved architecture-changing choices; a draft may proceed when user requests
    it, while implementation of dependent irreversible decisions waits for resolution.
    Do not invent surveys, KPIs, timelines or approval status. Never imply approval to build,
    spend, register services or deploy merely from completing a PRD.
    End with assumptions, evidence needed, owner and next decision. Review the riskiest flow
    and check requirement-to-acceptance traceability before delivery.
