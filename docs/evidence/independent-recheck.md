# Independent focused recheck

Date: 2026-10-12 (user timezone). Initial findings remain unchanged in `independent-review.md`; this file records the later hardened-edition retest.

Only inert temporary fixtures were used. No real credential file was opened, no target package/script was executed, no provider call was made, and no hosted deployment was contacted. Native Windows junctions were created inside a validated temporary root, removed as junctions, and then temporary directories were cleaned up. The production host is Windows with Python 3.13 and Node ESM.

## Retest outcomes

| Focus | Observed result | Status |
|---|---|---|
| Native child junction pointing outside target | All three `scan.py` copies returned `incomplete`, `files_read: 0`, and a skipped `junction` with reason `symlink/reparse directory not followed`. Outside dummy content was absent from output. | Initial high scope-escape finding fixed for this stable-tree case. |
| Linked target root and existing child under linked ancestor | All three scanners refused each with `target or ancestor is a symlink/reparse point; use an isolated regular tree`. | Pass for tested root/ancestor forms. |
| Dependency helper junction | `deps.py` returned incomplete, no manifest files, and `skipped_directories: ["junction"]`; linked root was refused. | Pass. |
| Dummy embedded credential assignment in ordinary source | All three scanners retained category/file/line with `[source content omitted; inspect cited line locally]`; the sentinel value was absent from serialized evidence. | Initial scanner disclosure finding fixed for tested source leads. |
| Known secret-bearing filenames | `.env` and `id_rsa` were explicitly skipped by all three scanners; scope became incomplete. Their dummy values were absent. | Pass. |
| Missing accounting plus failed verifier | Cap 100, synthesis reserve 10, concurrency 2, each slice upper bound 40: only two slices launched. Missing usage failed; verifier failure rejected; two subsequent slices skipped. Summary returned `measuredTotalTokens: 20`, `estimatedChargedTokens: 40`, `accountedTokens: 60`, `accountingComplete: false`. | Initial summary-accounting ambiguity fixed. |
| Complete measured accounting | A fully evidenced slice returned accepted, measured 20, estimated 0, accounted 20, `accountingComplete: true`. | Pass. |
| Observed adapter bound breach | A serial 40-token reservation returned actual usage 50: failed slice, `breached: true`, and next slice skipped. | Pass for observed breach; no claim of provider-side enforcement. |
| Standalone validation reference | The external relative link is gone. `tests/VALIDATION.md` now distinguishes bundled standalone tests from extra full-review-package tests and gives a local unittest command. | Initial broken/out-of-package link fixed. Claimed aggregate test counts were not independently rerun in this focused pass. |

## Remaining material issue

### High: dependency evidence still prints credential-bearing manifest values

The source-lead suppression does not cover `repo-evaluator/scripts/deps.py`. In an inert `package.json` containing a postinstall credential assignment and a dependency URL with userinfo credentials, `inspect(..., offline=True)` serialized both sentinel values unchanged. Relevant paths are `deps.py:70,73` and analogous source/requirement output at lines 81,97,109–111,130,141.

This is separate from the now-fixed source scanner. The helper is prescribed by the repository skill and `--json` prints its complete output; `--offline` prevents OSV calls but does not suppress local tool/transcript disclosure. The added platform warning to privately inspect/redact outputs before sharing accurately identifies the risk, but it cannot retroactively remove values already returned through a hosted agent's command result.

Fix: suppress raw script/URL/requirement values from default emitted evidence, retaining field location, category, source identity and sanitized host metadata. Use explicit private raw-output handling if needed for forensics. Avoid treating script output or URL redaction as complete merely because the source scanner omits matching lines.

## Smaller remaining clarity issues

The scheduler's aggregate fields now distinguish known and estimated usage correctly, but individual failed results still return the conservative estimate as `usage: 40` without an explicit per-result basis (`scheduler.mjs:56`). A consumer copying only task rows could still mislabel it as observed usage. Add `usageMeasured`/`usageBasis`, or separate `measuredTokens` and `chargedTokens` per row.

The budget reference still says "Release only after actual usage is returned" immediately before its missing-usage conservative-charge rule. Clarify that a reservation may close by conservatively charging its entire bound while actual accounting remains incomplete. The implementation follows the conservative rule in the tested case; this wording inconsistency does not undermine its tested admission arithmetic.

The new reparse guard is stable-tree inspection, not handle-based race resistance. Credential-bearing path names, git commit messages, parser exception text and other output surfaces remain separate review/privacy boundaries; this focused check does not establish universal secret redaction. Windows reparse variants beyond the native junction case and other operating systems were not runtime-tested here.

Conclusion: the focused fixes work on the exercised junction, source-output and aggregate-accounting cases. Dependency output still requires hardening before claiming the full helper workflow avoids embedded-credential disclosure.

## Final targeted recheck: dependency output and task-row accounting

Later changes were retested with fresh dummy fixtures, keeping all earlier observations as historical evidence. No network request was made; OSV candidate lists were inspected offline.

- Postinstall assignment, credential-bearing dependency source URL and unresolved requirements URL: their three dummy values were absent from serialized output. Manifest paths remained in `install_scripts`, `unusual_sources` and `notes` with omitted-content markers.
- A URL-valued npm lock version and a versioned Swift pin with userinfo credentials: both were omitted from advisory candidates and output; each generated a generic local-review note.
- Scheduler four-slice trial: missing usage and a thrown adapter error each became failed with charge 40 and `usageBasis: estimated-reservation`; a verified success and failed verifier each had actual usage 20 and `usageBasis: measured`, with accepted/rejected statuses respectively. Totals were measured 40, estimated 80, accounted 120, accounting incomplete. The per-row accounting ambiguity is fixed in these tested paths.

Two remaining dependency cases were discovered in this round:

1. A Swift `Package.resolved` pin containing only `state.revision` and a userinfo credential in `location` emitted that raw location in the no-version advisory note. Its candidate list was empty, but emitted evidence still contained the dummy value.
2. A versioned Swift `location` with `?access_token=<dummy>` remained unchanged in emitted `packages` and in OSV candidates. Offline mode prevented transmission in this test; the online path would use the same candidate identity.

These are credential-output/egress gaps in the same helper, not failures of the already passing scanner suppression. Suppress the raw no-version Swift location and reject or sanitize query/fragment/userinfo components before accepting a SwiftURL advisory identity. The results were sent to the parent for remediation.

Remaining privacy limits also include legitimate private package names/versions, internal host/path metadata, local file paths and report metadata. Omitting script/URL credential values does not anonymize package identities. Use offline mode for private package inventories and sanitize exported/shared artifacts; this review makes no claim of universal secret detection or anonymity.

## Closure recheck: remaining Swift URL cases

The later `deps.py` was independently retested against fresh inert `Package.resolved` fixtures. SHA-256 of the tested helper: `79d76cb550827c66ab81cd0f650f6c5765a159fbf6f4ae5df6a2db5fc199ee85`.

| Case | Serialized sensitive value | Advisory candidates | Outcome |
|---|---|---:|---|
| Revision-only pin, userinfo credential | Absent | 0 | Generic no-version note; raw location omitted. |
| Versioned pin, access-token query | Absent | 0 | Generic local-review note. |
| Versioned pin, token fragment | Absent | 0 | Generic local-review note. |
| Versioned pin, userinfo credential | Absent | 0 | Generic local-review note. |
| Ordinary versioned public-style URL | No sensitive value supplied | 1 | Ordinary advisory mapping remains available. |

Every case used `offline=True` and returned `osv.status: skipped_offline`; no advisory request or external target call occurred. Both remaining Swift disclosure/candidate defects are closed for the tested cases. The previous tables are historical observations, not current unresolved findings.

No additional material blocker was found in this exact closure scope. This statement is limited to the inspected helpers and exercised cases; package identities/metadata may still be private, malicious filesystem mutation is not race-proofed, and hosted security, real model compliance and provider-level economic enforcement remain unverified as already documented.
