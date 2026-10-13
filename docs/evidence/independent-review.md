# Independent forward-testing review

Date: 2026-10-12 (user timezone). Reviewer: independent reviewer agent.
Scope: the five local revised skills, their entrypoints, scenario-relevant references and helpers. The parent findings and build generator were not read. Only this report was written in the shared review package.

This is a static instruction review plus inert local helper testing, not a claim that a fresh production model followed these instructions. No target installation, target launch, live provider call, hosted MCP probe or billable delegation occurred. Fixtures used temporary directories and dummy strings; cleanup used native PowerShell and temporary-directory cleanup.

## Behavioral scenarios

| Scenario | Actual instructed outcome | Local evidence and achievable validation |
|---|---|---|
| Local skill ZIP containing traversal and a quoted attack example | Inspect before extraction; reject the archive before writing payloads; retain an incomplete/blocked assessment rather than treating rejection as proof of malware. A quoted attack is a contextual lead, not automatically a confirmed injection. | `safe_archive.unpack()` rejected `../outside.txt`. The fresh destination and escaped output were both absent. In a separate inert directory the scanner retained the quoted `ignore all previous instructions` example at line 2 and exited 0. Contextual dismissal must still be performed by the reviewer. The evidence contract explicitly distinguishes quotations at line 18. |
| stdio file MCP and hosted HTTP MCP source without deployment access | For stdio evaluate launch command, inherited credentials, OS authority and filesystem boundaries; do not invent a mandatory web login. For HTTP inspect authentication, authorization and transport controls in source while reporting hosted deployment configuration/operator practice unverified. Never connect merely to assess. | MCP entrypoint lines 28–35 and 44 implement those distinctions. `contained_file()` accepted a child file and rejected a sibling-prefix escape. Integer validation rejected booleans, partial numbers, zero/negative values, NaN strings and infinity. No HTTP service was contacted. A stable-tree path return is not a race-resistant file open or a deployment attestation. |
| Local repository with no git commit or gh authentication | Proceed with local static analysis and file hashes. Label provenance/incidents unknown and provide an unscored assessment, without fabricating a commit or demanding credentials. | Offline dependency helper exited 3 with `skipped_offline`; the local fixture had no `.git`. The score helper rejected an empty commit with exit 2 and `target.commit must be a full 40-hex revision`. The entrypoint/platform reference provide a valid unscored fallback; the calculator remains unsuitable for a hash-only artifact score. |
| User demands an immediate draft PRD and already settled the stack | Produce the requested draft in the requested format, use supplied context, honor the chosen stack, and expose consequential assumptions without a compulsory interview. Draft acceptance is proposed; creating the document does not authorize implementation or spending. | PRD entrypoint lines 11 and 43, questioning-patterns and template are consistent with that outcome. No stale vendor price is required for a useful initial draft: inaccessible changing costs must be unknown. Actual interview behavior, quality of the resulting PRD and requirement traceability were not model-executed here. |
| Concurrent delegation under a strict token ceiling, missing accounting, failed verifier | A true ceiling requires a trusted enforcing/accounting adapter. Without one, disclose advisory bounds or decline the strict run. Missing usage fails the slice; a failed verifier rejects its artifact; reservation headroom prevents further launches. | Inert scheduler: cap 100, reserve 10, concurrency 2, four slices each bounded at 40. Only `missing-usage` and `failed-verifier` launched. Missing usage became failed with conservative charge 40; verifier failure became rejected with measured usage 20; remaining two slices were skipped. `spentTokens` returned 60 and `breached:false`. No production cost enforcement or model quality was established. |

## Findings from the initial independent pass

### High: Windows junctions escape the scanner's target directory

`agent-skill-evaluator/scripts/scan.py:47–54` filters directories with `is_symlink()` only. The same algorithm is copied into the MCP/repository scanners; `repo-evaluator/scripts/deps.py:182–189` uses the same insufficient directory test. On this Windows/Python 3.13 host, a native NTFS junction is not a symlink and `os.walk(..., followlinks=False)` traversed it.

Reproduction: a temporary `source/junction` pointed to sibling `external`, containing only `inert.txt`. The skill scanner read the external file under the apparent relative path `junction/inert.txt`, emitted its dummy prompt-injection lead, and reported `status: complete`, `files_read: 1`, no skipped paths. This is a confirmed scope escape without a race or target-code execution. An arbitrary supplied directory can therefore expose unrelated files to evidence/transcript output and present them as target evidence.

Fix: refuse Windows reparse points/junction directories and files before traversal/open, record skipped paths as incomplete, and document/check the target-root and ancestor policy. A stable-tree guard is still not race-proof containment. Add a native inert Windows junction regression; POSIX symlink tests alone cannot catch this.

### High: raw lead output can disclose credential values

`agent-skill-evaluator/scripts/scan.py:97–99` stores the entire matching line as `text`; all three copied scanners emit the whole structure with `--json`. The evidence contract says not to copy live secret values into reports. An inert `AWS_SECRET_ACCESS_KEY=INERT_TEST_SENTINEL` fixture appeared unchanged in category 6 JSON. No live secret was used or opened during this test.

Risk: the required full evidence ledger and a tool transcript can contain actual embedded credentials; Windows scope escape makes this worse. A later prose instruction to redact does not undo earlier transcript disclosure.

Fix: avoid live secret-store files by default and redact sensitive assignment values, URL userinfo/query credentials and token patterns before rendering JSON/text. Keep path/line/category and a redaction marker. If raw forensic evidence is essential, make its private local-only handling explicit and keep it out of chat/public report output. Generic regex redaction is incomplete; report that residual limit.

### Medium: scheduler output conflates measured spend with conservative charges

`frugal-fable/scripts/scheduler.mjs:43–48,71` uses `charge=upperBound` after missing accounting, then combines it with returned usage into `spentTokens`; the missing slice also reports that estimate as `usage`. The trial's 60 equals 20 measured tokens plus an unmeasured 40-token reservation, not an observed 60-token provider spend. `breached:false` only means no observed bound breach; it cannot confirm compliance by an unaccounted adapter.

The prose correctly denies a provider-level ceiling without an enforcing adapter, and conservative admission arithmetic held in this test. The remaining defect is a machine-output assurance gap. Return measured usage and conservative charged/reserved estimates separately, include accounting-complete state and per-slice usage basis, and represent unobserved provider spend as unknown. The reference instruction "Release only after actual usage is returned" also needs an explicit conservative-charge exception to match implementation.

### Low: standalone skill validation link leaves its package

`repo-evaluator/tests/VALIDATION.md:3` points to `../../../../evidence/validation.json`. This is review-package evidence, not part of a separately copied/installed skill, and the relative depth does not identify the sibling `skill-review/evidence` location. Replace it with an accurate package-relative link plus an explicit standalone caveat, or bundle the evidence used for the claim inside the skill. No external evidence file was opened for this review.

## Contradictions and assurance limits

- The skills' prose expressly mentions reparse points and secret redaction, but the required scan helpers initially did not enforce those Windows/privacy boundaries. These are implementation defects, not objections to the conceptual checklist.
- Missing accounting becomes a failed slice; failed verification becomes rejected work. Neither is accepted. However conservative accounting is different from measured provider charges.
- The evidence contracts avoid universal SAFE verdicts and arbitrary safety percentages. The repository score keeps its deterministic legacy rubric, distinguishes coverage and severity, and rejects missing commits. That is internally coherent when the unscored fallback is respected.
- MCP mitigation examples explicitly limit stable-tree containment, DNS/redirect allowlisting, pseudonymization and subprocess/vm claims. No false race-proof or sandbox claim was found there.
- Package entrypoints/references are portable in intent and use ordinary Python 3.9+ (3.11+ for TOML) or Node ESM rather than a provider SDK. Host model discovery, permissions and accounting remain adapter responsibilities. POSIX legacy helpers and macOS artifact checks are explicitly scoped; they were not treated as native Windows tests.
- Four-space indentation of entrypoint bodies displays as code blocks in Markdown viewers. This is a readability issue, not a demonstrated model-execution defect. Normalize indentation if polished standalone skill documentation is intended.

## Remaining unknown unknowns worth preserving

Archive parser vulnerabilities, decompression CPU limits, hostile filesystem mutation and root/ancestor reparse points still require isolation or explicit limitations. Source revision identity is not deployment/package identity. A returned evidence path and `verifyPassed:true` are claims until reopened by the orchestrator. Two research votes may share a source or model failure mode. Token ceilings must cover orchestrator/retrieval/retry/verification/synthesis and distinguish estimated economics from observed accounting. PRD quality requires real task examples and traceability checks, not merely a complete template.

The initial package should not receive an unconditional validation sign-off until the confirmed scope and disclosure defects are fixed and rerun. This review provides local behavioral evidence only; it does not establish empirical malware-detection accuracy, portable behavior on untested operating systems, hosted security or production cost savings.
