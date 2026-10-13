# Budget and evidence contract
A reservation is the inclusive upper bound for one adapter call, including input,
output, cached/reasoning accounting, tool reads, nested model calls and retries.
The provider/runtime must enforce it for a true ceiling. The scheduler can detect a
breached contract after spending, but cannot undo a provider charge.
No parallel launch can reuse reserved headroom. Release only after actual usage is
returned. Missing usage fails closed by charging the whole reservation.
Failed calls count and consume their reservation conservatively; no automatic retry.
Reserve final synthesis explicitly; execute it as a separate accounted task.
Reject invalid/negative/NaN budgets, duplicate task IDs, unsafe paths and unknown tiers.
Record pending/running/completed/skipped/rejected/failed and why; exceptions are not nulls.
Evidence checks require a named artifact and verified acceptance. High-stakes review
cannot be missing. Reported passing tests still need the orchestrator to inspect evidence.
Research consensus records supporting, refuting, unknown and missing votes separately;
correlated votes do not increase independent-source count.


Outputs distinguish measuredTotalTokens, estimatedChargedTokens, accountedTokens
(their conservative sum), and accountingComplete. Missing usage/failed-call charges
are estimates, never reported as measured provider usage.
