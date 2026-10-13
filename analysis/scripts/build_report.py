"""Build an offline tabbed HTML report from source-bound findings."""
from pathlib import Path
import html
import json
import hashlib
import re
import zipfile
import difflib

BASE=Path(__file__).resolve().parents[1]
SRC=BASE/"original-snapshot"
NEW=BASE/"revised-skills"
esc=lambda x:html.escape(str(x),quote=True)

def fid(skill,path):return "source-"+skill+"-"+re.sub(r"[^a-zA-Z0-9-]","-",path)
def cite(skill,path,needle):
    lines=(SRC/skill/path).read_text(encoding="utf-8").splitlines()
    matches=[i+1 for i,l in enumerate(lines) if needle in l]
    if not matches:raise ValueError(f"Missing evidence: {skill}/{path}: {needle}")
    n=matches[0]
    return f'<a class="source-link" href="#{fid(skill,path)}-L{n}">{esc(path)}:{n}</a>'
def p(t):return "<p>"+t+"</p>"
def ul(items):return "<ul>"+"".join("<li>"+x+"</li>" for x in items)+"</ul>"
def table(headers,rows):
    return '<div class="table-wrap"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+v+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'
def section(number,title,body):
    return f'<section class="chapter"><div class="chapter-label">{number}</div><div><h3>{title}</h3>{body}</div></section>'
def flow(items):
    return '<ol class="flow">'+''.join('<li><span>'+esc(t)+'</span></li>' for t in items)+'</ol>'
def finding(skill,title,impact,path,needle,fix,residual,priority="Material"):
    return '<article class="finding"><div class="finding-head"><span class="tag">'+priority+'</span><h4>'+title+'</h4></div>'+p(impact)+'<div class="evidence">'+cite(skill,path,needle)+'</div>'+p('<strong>Revision:</strong> '+fix)+p('<strong>Remaining limit:</strong> '+residual)+'</article>'
def sources(skill):
    files=sorted(p for p in (SRC/skill).rglob("*") if p.is_file())
    body=''
    for path in files:
        rel=path.relative_to(SRC/skill).as_posix();data=path.read_bytes()
        lines=data.decode("utf-8").splitlines()
        body+=f'<details id="{fid(skill,rel)}" class="source-file"><summary>{esc(rel)} <small>{len(lines)} lines · SHA-256 {hashlib.sha256(data).hexdigest()[:12]}</small></summary><pre class="source-code">'
        for i,l in enumerate(lines,1):body+=f'<span id="{fid(skill,rel)}-L{i}"><b>{i:4}</b> {esc(l)}</span>\n'
        body+='</pre></details>'
    return f'<details class="source-collection"><summary>Original source evidence · {len(files)} files read in full</summary>{body}</details>'
def edition(skill):
    t=(NEW/skill/"SKILL.md").read_text(encoding="utf-8")
    return f'<details class="edition"><summary>Read the complete revised SKILL.md</summary><pre>{esc(t)}</pre></details><details class="edition"><summary>Review the exact source diff</summary><pre>{esc((BASE/"diffs"/(skill+".diff")).read_text(encoding="utf-8"))}</pre></details>'

SKILLS=[]

s="agent-skill-evaluator"
SKILLS.append(dict(id=s,name="Skill evaluator",full=s,version="Original v1.3.0 → local v2.0.0-review.1",
    thesis="It catches dangerous instructions, but its scanner can conceal missing evidence.",
    summary="Useful static triage. Revise acquisition, scanner completeness and verdict calibration before treating it as a dependable gate.",
    does=p("Reviews a third-party skill before installation: instructions, bundled code, hooks, network destinations, credential access, forced promotion and creator provenance. It produces an impact-first trust recommendation and a detailed report.")+
          p("The strongest original design choice is the boundary between <em>reading a skill</em> and <em>obeying it</em>. A security evaluator must treat the target’s instructions as evidence. Its scanner supplies leads; semantic inspection determines whether behavior is reachable and authorized.")+
          p(cite(s,"SKILL.md","Treat every downloaded file")),
    how=flow(["Acquire directory or .skill ZIP","Run eight-category Bash scan","Read instructions and supporting code","Research provenance and incidents","Assign dimension scores and severity floors","Deliver five-part verdict"])+
        p("The Bash scanner uses recursive grep, groups hits by file, and prints a preview. The main document insists on exhaustive instruction reading and resolving every lead. These procedural requirements are useful, but they cannot force an agent to comply or establish detection accuracy.")+
        table(["Component","Actual mechanism","Boundary"],[
            ["SKILL.md","Prompted workflow and subjective 0–100 scoring","Agent judgment; no deterministic score calculator"],
            ["scripts/scan.sh","Eight regex categories; one match preview per hit-bearing file","No parser/call-graph analysis; more than 60 files in a category can disappear"],
            ["References","Attack catalog and examples labelled safe","Some examples assert safeguards that code does not implement"],
            ["CHANGELOG.md","Reports past planted-fixture/field tests","Those fixtures are absent from this local package; claims are historical"]]),
    gaps="".join([
        finding(s,"A temporary directory does not prevent archive escape.",
            "The extraction advice claims a fresh temporary directory contains ../ entries, but no extractor validation is specified. An extractor that honors traversal can still write outside that directory.",
            "SKILL.md","this contains zip-slip",
            "Each revised evaluator includes the reviewed ZIP/TAR member validator: paths, links, special entries, collisions, count and expansion limits are checked before writing.",
            "Hostile parsers and concurrent filesystem mutation still require an isolated environment; refusal is not evidence of malware.","High"),
        finding(s,"The scanner discards leads and suppresses failures.",
            "The implementation suppresses grep errors and truncates to 60 hit-bearing files per category, despite saying every lead must be resolved. A failed read can resemble a no-hit scan, and buried files never reach the report.",
            "scripts/scan.sh","head -n 60",
            "Replaced the preview-only scan with a portable JSON ledger preserving all matches and reporting read errors, skipped paths, opaque content and explicit limits. A Bash compatibility entrypoint calls it.",
            "Regex completeness is still limited: semantic vulnerabilities and phrased/encoded instructions need manual review.","High"),
        finding(s,"Risk scores imply precision without a specified calculation.",
            "Five dimensions receive agent-assigned numbers; weights, aggregation, treatment of missing evidence and empirical calibration are unspecified. SAFE is stronger than static screening can establish.",
            "SKILL.md","Assign score (0-100)",
            "Use qualitative, evidence-bound verdict precedence; remove invented safety percentages and unqualified SAFE labels. Preserve unknowns prominently.",
            "Severity and reachability remain judgments; no adversarial precision/recall benchmark was run.","Material"),
        finding(s,"Capability is sometimes treated as automatic critical harm.",
            "Severity floors classify download-and-run as critical even if openly documented and explicitly requested. The attack reference similarly labels network/system access mechanically; context guidance elsewhere does not fully reconcile those rules.",
            "SKILL.md","Severity Floors",
            "Determine severity from authority, exposure, source-to-sink reachability and user impact. Distinguish benign examples, legitimate high-risk behavior, suspicious behavior and confirmed findings.",
            "Disclosure does not make a real flaw safe; intent is not required for vulnerability severity.","Material"),
        finding(s,"Examples labelled safe are not proof of containment.",
            "The reference calls an existence check path validation and presents cwd plus a timeout as sandboxing. A reviewed subprocess can still access the caller’s files, network and credentials.",
            "references/safe_skill_examples.md","cwd='/home/claude'",
            "Replace misleading examples with boundary conditions; require canonical component containment and state that timeout/cwd are not isolation.",
            "The revision supplies analysis guidance, not an operating-system sandbox.","Material"),
    ]),
    revised=p("A shorter entrypoint preserves the original trust behaviors and impact-first output. New self-contained helpers give portable full-lead scanning and validated archive extraction. The references now explain conditional safety rather than certifying snippets. Version metadata fits the local Codex skill validator.")+
        table(["Gap addressed","Concrete deliverable","Validation"],[
            ["Archive escape","scripts/safe_archive.py in each evaluator","Traversal rejected before any payload was written"],
            ["Hidden scan omissions","scripts/scan.py + scan-patterns.json","65 promo files retained; invalid UTF-8 and opaque files reported incomplete"],
            ["Instruction camouflage","Unicode leads also scanned in Markdown","Bidi marker fixture produced file/line evidence"],
            ["False assurance","evidence-contract.md and rewritten examples","Independent static scenario review; agent behavior remains a limitation"]])+edition(s),
    unknowns=table(["Blind spot / hypothesis","Why it matters to you","How the revision addresses it","Residual / learning test"],[
        ["A skill can fetch tomorrow’s instructions.","An unchanged local SKILL.md can lead to changed remote behavior.","Inventory transitive/remote dependencies and re-review changed hashes/endpoints.","Remote review is bounded to fetched snapshots; compare later artifacts."],
        ["The evaluator is itself a supply-chain dependency.","A compromised scanner can steal what it claims to protect.","Review/version/hash trusted helpers separately from target code.","Hashes establish identity, not benign behavior; use immutable snapshots."],
        ["Review files can become an injection channel.","Quoted attacks or HTML may be executed or obeyed during reporting.","Treat evidence as data; this report escapes all source text.","Do not render arbitrary target HTML/Markdown as active content."],
        ["Absence of reputation is not evidence of harm.","A new useful solo project may have no public discussion.","Keep provenance unknown and popularity weak.","Prefer reproducible behavior and transparent ownership."],
        ["A version banner can be false.","An agent can print a version without actually loading that file.","Bind source manifest hashes and inspected artifacts.","Runtime logs/permissions require observation, not self-report."],
    ])+p("<strong>Useful experiment:</strong> keep a held-out corpus of benign capabilities and malicious behaviors, then measure both false positives and missed findings. Repeating the author’s planted examples tests memorization more than generalization."),
    prompt="Use agent-skill-evaluator from this revised folder to statically assess the supplied skill. Preserve its exact revision or file hashes. Read all instruction files, retain full scan JSON, never run the target, and report each material finding with reachability, evidence, mitigation and unread scope. Produce HTML; do not invent a safety percentage."
))

s="mcp-evaluator"
SKILLS.append(dict(id=s,name="MCP evaluator",full=s,version="Original unversioned → local v2.0.0-review.1",
    thesis="Its “safe” references contain unsafe boundaries—and its MCP-specific coverage is too thin.",
    summary="Prioritize this revision. Generic code review is useful, but it needs transport-aware authorization, tool trust boundaries and corrected examples.",
    does=p("Reviews an MCP server’s stated function, code, privacy, maintenance, alternatives and usability before a user chooses it. MCP exposes tools, resources and prompts to an AI client, so the real question is which authority an untrusted input can obtain through those interfaces.")+
          p("The original review favors GitHub access and community search, asks for Markdown/PDF, and assigns five subjective dimension scores. It contains no executable scanner or tests of its own."),
    how=flow(["Fetch repository metadata and selected code","Describe server and external APIs","Search alternatives and community","Match code against reference patterns","Score security/privacy/reliability/usability","Recommend installation"])+
        p("The main workflow gives authentication, logging and input validation broad attention. It does not establish a static-only execution boundary, exact deployed revision or complete review inventory. Its concrete recommendations depend heavily on the supplied reference snippets.")+
        p("For protocol guidance, this report checked the official <a href='https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices'>MCP security guidance</a> and <a href='https://modelcontextprotocol.io/specification/2025-11-25/basic/transports'>transport specification</a>, using the named 2025-11-25 baseline rather than claiming it is the latest possible version."),
    gaps="".join([
        finding(s,"The filesystem “safe” example accepts a sibling prefix.",
            "With an allowed root /data, a resolved path /data-private/secret begins with /data and passes startsWith. The snippet also lacks protection against a symlink pointing outside the root.",
            "references/safe_mcp_examples.md","filePath.startsWith",
            "Replace the example with a tested Python helper that resolves paths and uses component containment; it rejects sibling traversal and a resolved symlink escape.",
            "Validation followed by open is still a time-of-check/time-of-use boundary; hostile writers require OS-enforced isolation or handle-based access.","High"),
        finding(s,"Node vm is explicitly not a security sandbox.",
            "The reference labels vm.runInContext safe for code execution. A timeout and curated globals do not turn that module into a boundary for hostile code. <a href='https://nodejs.org/api/vm.html'>Node’s own documentation states this limitation.</a>",
            "references/safe_mcp_examples.md","SAFE - VM with",
            "Remove the sandbox claim and require an actually enforced isolation boundary for any authorized dynamic test.",
            "No production code-execution sandbox was implemented or validated in this task.","High"),
        finding(s,"HTTP and stdio have different authentication models.",
            "A ListTools handler without an auth check is labelled high severity without specifying transport or surrounding middleware. Local stdio authority and exposed HTTP identity/authorization must be assessed differently.",
            "references/mcp_security_patterns.md","Pattern: Missing Authentication",
            "Add transport-aware review of HTTP Origin/local binding, identity, per-resource/user authorization, audience/scopes, token passthrough, OAuth state/consent and session isolation.",
            "Source cannot prove that a hosted instance deploys the reviewed configuration; report that scope separately.","High"),
        finding(s,"Privacy and reliability examples overclaim their protection.",
            "A deterministic hash of a username is called anonymous; log redaction only inspects top-level keys; and retry-with-backoff repeats every operation even if it already charged money or sent a message.",
            "references/safe_mcp_examples.md","user_hash: hashedId",
            "Treat the hash as pseudonymous, prefer avoiding sensitive payload logs, examine nested/error flows, and require idempotency for mutation retries.",
            "These are corrected review requirements, not an implementation of a logging system or payment adapter.","Material"),
        finding(s,"The credential/configuration examples contain correctness bugs.",
            "On its first-key branch, Fernet.generate_key returns bytes, then the code calls key.encode(). Numeric config uses parseInt and only checks upper bounds; negative values, NaN and partial strings can escape validation.",
            "references/safe_mcp_examples.md","key = Fernet.generate_key()",
            "Remove the faulty keyring snippet, document bytes/string normalization, and supply strict positive-integer validation with meaningful edge-case tests.",
            "Keyring/Fernet integration itself was not exercised; the numeric helper was.","Material"),
        finding(s,"Assessment outputs and scores are not portable or calibrated.",
            "The skill assumes create_file and /mnt/user-data/outputs and encourages confident scores without a defined aggregate or uncertainty gate. Usability should not numerically compensate for a serious security flaw.",
            "SKILL.md","Use built-in",
            "Respect available filesystem/output tools, use revision-bound coverage and qualitative security verdicts, and separate reliability/usability from security.",
            "Qualitative judgment still needs evidence; no deployed server was probed.","Material"),
    ]),
    revised=p("The new entrypoint adds static acquisition, source/deployment separation, tool-schema and description trust, transport-aware checks, data-flow mapping, bounded resources, and explicit uncertainty. Both old reference files are replaced. New helpers provide static leads, safe archive extraction and tested boundary examples.")+
        table(["Concrete change","Evidence of validation"],[
            ["contained_file: canonical path components","Allowed child accepted; sibling-prefix and symlink escape refused"],
            ["positive_integer: complete bounded integer","NaN, infinity, booleans, zero, negatives and partial strings rejected"],
            ["Transport/MCP checklist","Compared with official protocol baseline; independently scenario-reviewed"],
            ["Report contract","Source review cannot masquerade as hosted-deployment validation"]])+edition(s),
    unknowns=table(["Blind spot / hypothesis","Why it matters to you","Addressed in revised workflow","Residual / learning test"],[
        ["A harmless tool description can change after approval.","The same tool name may request different authority later.","Pin/review descriptors, scopes and deployment changes.","Recheck descriptor snapshots before later use; no runtime monitor supplied."],
        ["Tool outputs can instruct another tool to act.","One low-risk data source can influence a powerful tool.","Treat results as data; inspect cross-tool instruction/approval boundaries.","Test client behavior with inert hostile descriptions in an isolated environment."],
        ["OAuth metadata discovery is itself network access.","A malicious URL can target local/cloud metadata.","Review redirects, DNS rebinding, internal ranges and egress policy.","Connection-time policy needs implementation/deployment evidence."],
        ["An annotation is not an enforcement mechanism.","A declared read-only tool may write, leak or spend.","Trace actual sinks and server/client permission checks.","Check implementation and effective client policy independently."],
        ["A timeout does not mean the mutation failed.","Retry can duplicate an external effect.","Record idempotency/cancellation and reconcile uncertain outcomes.","Test interrupted writes using dummy endpoints and operation IDs."],
        ["Local trust changes behind a proxy.","A stdio process exposed via HTTP acquires a different threat model.","Examine proxy identity, session separation and inherited authority.","Source-only review cannot confirm live proxy configuration."],
    ])+p("<strong>Design suggestion:</strong> model each tool as a capability with an explicit resource scope, budget and allowed effect. Review the composition of capabilities, not only individual function bodies."),
    prompt="Use the revised mcp-evaluator to assess this server before connecting it. State stdio/HTTP transport, source revision and deployment visibility. Trace tool arguments to sensitive sinks, inspect MCP authorization and instruction boundaries, and report unknown deployment controls separately. Static review only; deliver evidence-backed HTML."
))

s="repo-evaluator"
SKILLS.append(dict(id=s,name="Repository evaluator",full=s,version="Original v1.2.1 / rubric 1.1.0 → local v1.3.0-review.1 / same rubric",
    thesis="The best-engineered evaluator here. Preserve its scoring system; repair portability and evidence limits.",
    summary="Keep the 22-check policy. The meaningful gaps are Windows execution, paths, authentication rigidity and sampled artifact/provenance boundaries.",
    does=p("Screens general software before installation: installer/build entrypoints, runtime behavior, credentials, data transfer, persistence, dependencies, package provenance, maintainers and agent-facing instructions. It separates source from the binary or package a user would install.")+
        p("Unlike the sibling evaluators, this one has a machine-readable rubric, input validation, a deterministic calculator, explicit unknowns and an offline regression suite. Its score is a <em>reviewed-evidence score</em>, not a probability of safety."),
    how=flow(["Identify exact install path/version","Fetch isolated public Git source","Scan code and dependencies; collect provenance","Read sensitive code; resolve leads","Fill 22-check evidence ledger","Calculate score + coverage + severity cap"])+
        table(["Dimension","Weight /100","Mechanism"],[
            ["Installation","10","Install entrypoints, privilege, persistence"],
            ["Code behavior","30","Entrypoints, execution, credentials, destruction, concealment"],
            ["Data/privacy","20","Network, telemetry, collection"],
            ["Supply chain","20","Dependencies/advisories, artifact, updates"],
            ["Source trust","10","Identity, maintenance, independent incidents"],
            ["Transparency/agent safety","10","Disclosure, promotion, removal, agent instructions"]])+
        p("Pass earns the check’s weight; concern earns half; failure earns none. Unknowns leave the assessed denominator and reduce coverage. Medium/high/critical findings cap the score at 69/49/29. Evidence judgments remain human/agent inputs.")+
        '<div class="calculator"><h4>Why score and coverage must travel together</h4><label for="coverage">Illustrative assessed weight: <output id="coverage-out">4</output> /100</label><input id="coverage" type="range" min="1" max="100" value="4"><div class="calc-row"><strong id="score-demo">100 /100</strong><span id="coverage-demo">4% weighted coverage</span></div><p>Assume every assessed check passes and the rest stay unknown. The score stays 100 while coverage changes. This illustration is arithmetic, not a target evaluation. A few easy passes cannot justify installation.</p></div>',
    gaps="".join([
        finding(s,"Windows evidence paths break inventories and tests.",
            "scan.py stores str(relative_path), which uses backslashes on Windows, while workflow/instruction detection tests expect forward-slash prefixes. deps.py similarly emits backslash manifest provenance. Two original tests failed on these differences here.",
            "scripts/scan.py","rel = str(path.relative_to(root))",
            "Normalize evidence paths with as_posix() and use explicit UTF-8 reads in Python helpers. Add a test for Windows CI-workflow and agent-instruction inventories.",
            "Filesystem reparse points/live path races remain outside guarantees; use immutable isolated trees.","Material"),
        finding(s,"Bare bash is not a portable Windows command.",
            "This machine resolves bash to the Windows system launcher. Four original shell-invoking fixtures fail through shell/path behavior; macOS validation does not validate the Windows invocation.",
            "tests/test_evaluator.py","['bash',str(ROOT/'scripts/scan.sh')",
            "Use direct Python scan/dependency commands and add a public-GitHub Python fetcher. Adapt one CLI test to Python; mark three POSIX shell-only fixtures skipped on Windows and test replacements separately.",
            "Legacy artifact inspection remains macOS-oriented. Native Windows Authenticode and live fetch are not validated.","Material"),
        finding(s,"Authentication is an unnecessary hard stop for local review.",
            "The preflight stops all work if gh auth fails. That prevents useful static review of already supplied local source, even though code scanning and scoring mechanics do not need GitHub access.",
            "SKILL.md","If it fails, stop",
            "Continue bounded offline/local analysis with unavailable provenance unknown. A source tree without a verified commit gets an unscored evidence assessment; never fabricate the SHA required by score.py.",
            "A revision-bound scored report still needs a corroborated revision and actual evidence for assessed checks.","Material"),
        finding(s,"A complete rubric is not a complete security audit.",
            "The calculator validates the shape of evidence, not whether that evidence is genuine or representative. A 100 score from 4% assessed weight is possible by design and explicitly tested.",
            "tests/test_evaluator.py","test_sparse_review_never",
            "Keep the rubric unchanged and preserve score/coverage/provisional status together. Reiterate evidence scope and avoid comparing different coverages as equivalent.",
            "Weights/thresholds remain policy choices without empirical calibration. This task does not claim a new calibrated scoring model.","Interpretation"),
        finding(s,"Artifact/provenance helpers sample more than their labels imply.",
            "inspect_artifact.sh examines only selected targets/files and has whitespace-sensitive xargs file input. repo_meta.py uses first-page contributor totals and heuristic fork/star comments; registry lookup prints linkage metadata rather than proving exact-version equivalence.",
            "scripts/inspect_artifact.sh","xargs file",
            "Document the legacy artifact wrapper as sampled and require independent interpretation of omitted paths, command failures and exact install artifact. Contributor statistics stay sample-only; registry linkage must be compared manually.",
            "The legacy wrapper and metadata sampling are documented/mitigated, not comprehensively rewritten or live-validated.","Material"),
    ]),
    revised=p("The local edition keeps rubric 1.1.0 and score.py’s arithmetic. It fixes Python paths/encoding, adds a portable fetcher with isolated Git configuration and argument validation, documents offline behavior, and makes platform test boundaries visible.")+
        table(["Observed result","Scope"],[
            ["Original: 56 tests; 50 passed, 6 failed","Current Windows/Python 3.13 run; see original-windows-tests.txt"],
            ["Revised: 56 tests; 53 passed, 3 skipped","Legacy POSIX shell cases are explicit skips, not passes"],
            ["New package regressions: 15 passed","Includes mocked fetch isolation, Windows junctions, credential-safe output, Swift URL exclusions and inventory paths"],
            ["Rubric unchanged","No rescoring of a real target and no installation approval implied"]])+edition(s),
    unknowns=table(["Blind spot / hypothesis","Why it matters to you","Revision treatment","Residual / learning test"],[
        ["The release can differ from Git source.","A reviewed repository may not contain the payload you install.","Keep exact install artifact/source linkage a separate rubric check.","Optional artifact inspection does not prove reproducible build equivalence."],
        ["Known-advisory absence is not code safety.","A new attack or unused/feature-specific dependency can evade simple lookup.","Report parsed candidates, unsupported locks and applicability separately.","Use a feature/target-resolved dependency graph and source inspection where needed."],
        ["Advisory queries can reveal a private stack.","Package names/versions may identify proprietary work.","Offer offline mode; name what OSV receives.","Privacy boundary is a real data-flow decision, not just secret-value redaction."],
        ["Literal domain scans miss constructed destinations.","Dynamic URL assembly, native sockets and dependencies evade regex.","Trace sensitive call sites and disclose inventory limits.","A domain list is not a full network graph."],
        ["Evidence is valid only for a particular moment.","An auto-update, ownership change or new dependency bypasses past review.","Specify re-review triggers and preserve hashes/revision receipts.","No live update monitor was created."],
        ["Concentration statistics can be biased by pagination.","First 100 contributors are not the whole contributor population.","Treat helper outputs as sampled clues and independently verify material claims.","Do not turn stars, forks or identity into a safety threshold."],
    ])+p("<strong>Analytical suggestion:</strong> use a vector of evidence coverage, reachable impact and reversibility alongside the scalar score. The scalar helps consistency; the vector protects you from false comparability."),
    prompt="Use the revised repo-evaluator on this exact software/install path. Preserve the current rubric, retain complete scan/dependency evidence, and show score with weighted coverage, unknowns and severity caps. If source has no verified commit, produce an unscored assessment. Do not install/build/run the target; report platform and artifact limits."
))

s="prd-creator"
SKILLS.append(dict(id=s,name="PRD creator",full=s,version="Original unversioned → local v2.0.0-review.1",
    thesis="Strong discovery habits; weakened by contradictory examples and interview quotas.",
    summary="Keep conversational discovery and build-versus-buy. Replace rigid pacing with material uncertainty and traceable acceptance.",
    does=p("Turns a product idea into one requirements document through guided discovery, trade-off education and research. It covers eleven areas, including flows, users, data, roles, integrations, constraints and costs, then writes acceptance criteria and open assumptions.")+
        p("For a solo AI builder, its value is preventing an agent from building a plausible product that solves the wrong problem. The PRD is a decision record and verification contract; it is not automatic permission to build or deploy."),
    how=flow(["Read existing context","Explore eleven discovery areas","Discuss platform/data/auth/build-or-buy","Research costs and technical limits","Summarize and confirm, or draft with assumptions","Populate one PRD and iterate"])+
        p("The main file is thoughtful about depth and user education. The references supply a lengthy template, conversation patterns, three fictional PRDs and provider-specific tool instructions. Problems arise where these references contradict the entrypoint or demonstrate weaker requirements than they request."),
    gaps="".join([
        finding(s,"Question quotas can obstruct an already clear request.",
            "The reference demands at least ten questions before generation. The entrypoint allows a user to request an immediate draft. Enough supplied context may already resolve material decisions; counting messages is not a readiness criterion.",
            "references/questioning-patterns.md","Minimum: 10 questions",
            "Track areas as known, material unknown, provisional assumption or N/A. Ask only questions that can change a meaningful decision and honor requests for a draft.",
            "Irreversible dependent implementation still waits for required unresolved choices; drafting and execution are different actions.","Material"),
        finding(s,"The examples contradict the no-code requirement.",
            "The main skill prohibits actual code in the PRD, while output-examples.md includes CSS and tells beginners to include code examples/tutorials. This encourages copying implementation into a requirements artifact.",
            "SKILL.md","Never put actual code",
            "Replace the examples and template with conceptual schemas and observable acceptance criteria. Implementation choices remain proposed unless confirmed.",
            "A PRD may specify a chosen technology when the user requires it; it should not silently constrain replaceable details.","Material"),
        finding(s,"Research guidance compares unlike services.",
            "A payment-processing example lists AWS SES alongside Stripe. Amazon SES is an email service, so this is a category error in a reference meant to educate the user. <a href='https://aws.amazon.com/ses/'>AWS describes SES as an email service.</a>",
            "references/tool-integration.md","AWS SES",
            "Require comparisons among substitutes serving the same function and favor official sources; remove the faulty example.",
            "Actual product/vendor choices need project-specific current research; none were selected here.","Material"),
        finding(s,"A detailed document can still launder invented evidence.",
            "Example PRDs state invented survey percentages, adoption goals, schedules, approval status and free-tier sufficiency. Although presented as examples, their unsupported precision can be carried into real output.",
            "references/output-examples.md","User surveys show 67%",
            "Explicitly mark fictional examples, distinguish proposed/confirmed facts, attach source/status to requirements and timestamp changing cost assumptions.",
            "The agent must still verify facts; a label alone does not validate a real survey or cost model.","Material"),
        finding(s,"Coverage lacks a closed requirement-to-verification chain.",
            "The template offers many sections, but does not consistently bind each requirement to an originating fact, owner, acceptance criterion and validation method. Generic metrics or architecture can look implementation-ready while remaining untestable.",
            "references/prd-template.md","FR-1.1",
            "Stable requirement IDs, source/status, priority, measurable acceptance and verification; explicit data lifecycle, operations and risk-learning tasks.",
            "Acceptance criteria are proposed until confirmed; real execution and product research remain separate.","Material"),
    ]),
    revised=p("The revised skill keeps discovery, education, build/buy/configure and one right-sized document. It removes interview quotas and provider-specific tool assumptions, aligns all four references, and adds traceability, lifecycle/operations, cost-source metadata and an AI-specific branch only when relevant.")+
        table(["Original risk","Revision behavior"],[
            ["User says ‘draft now’","Draft with visible assumptions; no compulsory ten-question detour"],
            ["User gives a settled stack","Respect it; ask only material compatibility or risk questions"],
            ["AI product has external actions","Specify authorized effects, evaluation, retention, costs and fallback"],
            ["Solo local tool","No reflexive cloud/auth/microservices requirements"]])+edition(s),
    unknowns=table(["Blind spot / hypothesis","Why it matters to you","Revision treatment","Residual / learning test"],[
        ["Building the wrong thing efficiently is still failure.","An excellent AI implementation may lack a real user problem.","Keep observed problem evidence separate from proposed outcomes.","Interview/observe a user or test a tiny prototype before expensive architecture."],
        ["Vendor lock-in hides in export and operational burden.","Cheap entry pricing can create expensive migration or maintenance.","Record exit cost, export/restore and dependency ownership.","Perform one round-trip export/import before adopting the data model."],
        ["AI quality needs a dataset, not a clever demo.","Prompts that work on one example can fail silently later.","Define observable evaluation and failure/fallback behavior for AI features.","Use held-out representative cases; don't optimize only for the demo."],
        ["An agent can confuse a spec with authority.","A PRD mentioning email/payment/deployment can trigger actions.","Separate requirements from authorization to build, spend or publish.","Keep operational permissions in the task execution boundary."],
        ["Concurrency and retries alter product semantics.","Double taps, delayed sync and retries create duplicate or lost records.","Specify edge behavior, ownership and idempotency where applicable.","Test duplicate requests and restore/conflict behavior."],
        ["A success metric can reward the wrong behavior.","Engagement or token volume may worsen the user's actual outcome.","State user outcome, workload and measurement method.","Pair the metric with a counter-metric such as error or intervention rate."],
    ])+p("<strong>Useful principle:</strong> spend the next question on reducing decision uncertainty, not filling a template. For a consequential unknown, define the cheapest experiment that could change your architecture."),
    prompt="Use the revised prd-creator to write a right-sized PRD from my supplied context. Respect settled choices. Ask only material unanswered questions; if I request a draft, mark assumptions openly. Every requirement needs a stable ID, source/status, measurable acceptance and validation method. Deliver HTML and treat build/deployment authorization separately."
))

s="frugal-fable"
SKILLS.append(dict(id=s,name="Frugal delegation",full=s,version="Original unversioned → local v2.0.0-review.1",
    thesis="Good orchestration advice. Its cost and verification claims exceed what the code enforces.",
    summary="Preserve file-based handoffs and strong integration. Replace stale harness/model assumptions with tested, provider-neutral scheduling.",
    does=p("Keeps a premium orchestrator on architecture, decomposition and final review while routing repeatable work to cheaper models. It uses bounded handoff packets, model tiers and scratch files to reduce orchestrator context traffic. An optional external Codex lane uses another provider/account boundary.")+
        p("The economic benefit is a hypothesis, not a property of choosing a cheap model. Coordination, repeated context, failed patches, retrieval and final integration can exceed the token savings."),
    how=flow(["Decompose into independent slices","Select capability floor","Write ownership/scratch/verification packet","Delegate via Agent or custom Workflow","Return short summary plus artifact path","Review evidence and integrate"])+
        p("The research JavaScript caps angles, sources and verification count. It uses an estimated output budget and agent-voting filter. The fanout template dispatches workers and optional verifiers through harness-provided globals, not standard JavaScript APIs.")+
        table(["Bundled artifact","Actual behavior"],[
            ["frugal-research.js","Output usage × assumed I/O ratio estimates total; calls are concurrent; synthesis pinned to Sonnet"],
            ["fanout-template.js","Unknown tier falls to Haiku; failed/missing verifier may evade flagged list"],
            ["codex-delegation.md","Hardcoded July 2026 model IDs, POSIX CLI recipes, quota claims and resume assumptions"],
            ["routing-cheatsheet.md","Sound file handoffs, but research advice points to an external uncapped workflow"]]),
    gaps="".join([
        finding(s,"The advertised hard total-token cap is an estimate.",
            "The code admits budget.spent counts output only and applies a fixed 10× ratio to estimate total tokens. Parallel calls check the same available headroom without reserving their potential cost; synthesis also adds work after that gate.",
            "references/frugal-research.js","budget.spent() counts OUTPUT tokens only",
            "Replace the proprietary workflow with a provider-neutral scheduler that reserves inclusive upper bounds synchronously before dispatch, bounds calls/concurrency, and accounts actual usage.",
            "A true provider spend ceiling requires an enforcing adapter; post-call detection cannot reverse a charge. No live provider adapter or hard monetary cap is supplied.","High"),
        finding(s,"Disputed evidence becomes “confirmed.”",
            "With two valid votes, the claim survives unless both refute it. A 1–1 disagreement enters the confirmed set and the synthesis prompt sees only surviving claims.",
            "references/frugal-research.js","refuted < REFUTATIONS_REQUIRED",
            "Keep supported-pending-source-review, disputed, refuted and unknown distinct; never call survival confirmation. Independent-source verification remains the orchestrator's job.",
            "Two agents often share models/sources/errors; vote count is not a calibrated confidence measure.","High"),
        finding(s,"Missing verification can look successful.",
            "fanout-template.js flags only a truthy verdict with sound=false. A null verdict is not flagged. verifyPassed is optional and is not used to reject acceptance; an unknown tier is silently routed to Haiku.",
            "references/fanout-template.js","r.verdict && !r.verdict.sound",
            "Validate tiers and task schema; require evidence plus passing requested verification and high-stakes review. Missing/failed verification rejects the candidate.",
            "An evidencePresent boolean is still a report, not authenticated proof; the orchestrator must inspect artifacts.","High"),
        finding(s,"Availability and quota assumptions are not portable.",
            "Workflow, agent, pipeline and budget are custom harness globals. Model IDs and quota generosity are frozen in a July reference; current capability availability and account limits vary.",
            "references/codex-delegation.md","Current model mappings",
            "Discover live tools/model IDs locally, preserve user settings, use capability labels, and expose adapter requirements. Remove unsupported quota guarantees.",
            "Cross-provider CLI execution and savings were not tested; account usage can include work outside this scheduler.","Material"),
        finding(s,"A content-derived scratch slug is not a unique run.",
            "The research scratch path depends on a truncated question slug. Repeating a question or overlapping runs can mix evidence, and returned paths are trusted without a contract check.",
            "references/frugal-research.js","const SCRATCH",
            "Require unique run IDs, validated returned paths and disjoint ownership. Prevent traversal and unexpected output paths in the scheduler.",
            "The scheduler checks lexical paths only; the adapter must enforce filesystem containment, no symlink escape and actual uniqueness.","Material"),
        finding(s,"The template undercuts its own premium-judgment rule.",
            "The entrypoint says final synthesis stays with Fable; the research script pins it to Sonnet and calls that a cost guarantee. A high-stakes Opus worker can be checked by a lower-tier Sonnet verifier.",
            "SKILL.md","Final review, risk assessment",
            "Keep final judgment with the orchestrator and use a verifier capability floor appropriate to stakes. Account synthesis explicitly, with reserve rather than hidden cost.",
            "No benchmark establishes an optimal routing policy; demonstrate quality and total cost on representative tasks.","Material"),
    ]),
    revised=p("The portable replacement retires both proprietary Workflow scripts in this review copy and supplies scripts/scheduler.mjs. It has no embedded provider calls. A configured adapter can use available authorized tools; the scheduler enforces admission reservations and candidate-evidence gates.")+
        table(["Invariant tested","Result"],[
            ["Concurrent reservations cannot reuse the same headroom","Passed using a delayed mocked adapter"],
            ["Missing usage is not zero-cost success","Whole reservation charged conservatively; call fails"],
            ["Reservation breach stops later launches","Detected and reported; in-flight work may already exist"],
            ["Missing verification/failed review/stopped work","Rejected"],
            ["Invalid budgets/unknown tiers/duplicate IDs/unsafe paths","Rejected"],
            ["Split/missing research votes","Disputed or unknown, never confirmed"]])+edition(s),
    unknowns=table(["Blind spot / hypothesis","Why it matters to you","Revision treatment","Residual / learning test"],[
        ["Token savings can increase total cost.","Cheaper work can require repeated premium repairs.","Account dispatch, repeated context, retries, verification and integration.","Compare measured total tokens/dollars and acceptance quality against direct work."],
        ["Parallel verification is statistically correlated.","Two agreeing agents may just repeat one source.","Track evidence and independent provenance separately from votes.","Use distinct evidence, not merely another sampler."],
        ["An external CLI changes data custody.","More quota may send private source/context to another provider.","Respect authorization and disclose named shared slices.","Provider retention/account policy must be checked for the actual lane."],
        ["Successful workers can still overwrite each other.","Shared filesystem plus stale patches defeats good individual output.","Disjoint ownership, current-diff integration and unique output locations.","Use isolated worktrees for coupled file ownership; none are needed for this package."],
        ["Cached/input/reasoning usage complicates accounting.","Output tokens alone do not price or measure quota.","Require inclusive usage from the adapter; otherwise disclose estimates.","A strict ceiling needs actual enforcement, not a multiplier."],
        ["Stopping too early can be as costly as over-research.","A blanket ban on gap-fill can leave necessary work unfinished.","Reserve essential integration/verification inside agreed scope.","Escalate only material scope/budget changes; do not silently abandon acceptance."],
    ])+p("<strong>Break-even model:</strong> delegation helps only if C<sub>dispatch</sub> + ΣC<sub>worker</sub> + C<sub>verify</sub> + C<sub>integrate</sub> + E[C<sub>rework</sub>] &lt; C<sub>direct</sub>, at comparable acceptance quality. Measure the entire chain."),
    prompt="Use revised frugal-fable only for authorized independent slices. Discover available models/tools; assign disjoint ownership and unique scratch paths. Plan inclusive usage and final review reserve. Require evidence and successful verification before acceptance. If the runtime cannot enforce total-token bounds, call the budget advisory and do not promise a hard cap."
))

def main():
    repo=next(s for s in SKILLS if s["id"]=="repo-evaluator")
    repo["gaps"]+=finding("repo-evaluator","Windows junctions and raw source lines cross privacy boundaries.",
        "The original Python scanner checks is_symlink, which does not catch Windows directory junctions, and emits whole matching lines in JSON. An independent inert test of the copied helper traversed a junction and exposed a credential-assignment sentinel. The same directory predicate is present in the original dependency walker.",
        "scripts/scan.py","if path.is_symlink():",
        "All three Python scanner editions now refuse linked/reparse roots and skip junction directories as incomplete. They retain category/file/line but omit matching source content; known credential-bearing filenames are not opened. The dependency walker and archive ancestor checks also reject reparse points.",
        "A concurrently changing hostile filesystem remains outside guarantees. Raw script/source/unresolved-requirement values are omitted from dependency output, but package identities and metadata can still be private; review those before sharing.","High")
    for s in SKILLS:
        if s["id"] in {"repo-evaluator","agent-skill-evaluator","mcp-evaluator"}:
            s["revised"]=p("<strong>Independent-review correction:</strong> the copied repository helpers initially inherited a Windows junction escape and raw-line disclosure. Focused reparse-point and credential-sentinel regressions now pass. Scan ledgers preserve every lead location while omitting source-line content; skipped credential files remain visible scope gaps. The repository dependency helper also omits raw script, source-URL and unresolved-requirement values.")+s["revised"]
        if s["id"]=="frugal-fable":
            s["revised"]=p("<strong>Accounting correction:</strong> scheduler output separates measuredTotalTokens, estimatedChargedTokens, accountedTokens and accountingComplete. Each task row labels its usageBasis. Missing provider usage is conservatively charged, explicitly estimated, and never described as measured spend.")+s["revised"]
    manifest=json.loads((BASE/"evidence/source-manifest.json").read_text(encoding="utf-8"))
    validation=json.loads((BASE/"evidence/validation.json").read_text(encoding="utf-8")) if (BASE/"evidence/validation.json").exists() else {}
    for entry in manifest:
        actual=(BASE/"original-snapshot"/entry["path"]).read_bytes()
        if hashlib.sha256(actual).hexdigest()!=entry["sha256"]:raise ValueError("Original changed: "+entry["path"])
    (BASE/"packages").mkdir(exist_ok=True)
    for s in SKILLS:
        with zipfile.ZipFile(BASE/"packages"/(s["id"]+".zip"),"w",zipfile.ZIP_DEFLATED) as z:
            for f in sorted((NEW/s["id"]).rglob("*")):
                if f.is_file() and "__pycache__" not in f.parts and f.suffix!=".pyc":
                    z.write(f,f.relative_to(NEW).as_posix())
    with zipfile.ZipFile(BASE/"packages/revised-skills.zip","w",zipfile.ZIP_DEFLATED) as z:
        for f in sorted(NEW.rglob("*")):
            if f.is_file() and "__pycache__" not in f.parts and f.suffix!=".pyc":z.write(f,f.relative_to(NEW).as_posix())
    tabs=''.join(f'<button type="button" role="tab" id="tab-{s["id"]}" aria-controls="{s["id"]}" aria-selected="{"true" if i==0 else "false"}" tabindex="{0 if i==0 else -1}">{s["name"]}</button>' for i,s in enumerate(SKILLS))
    panels=''
    for i,s in enumerate(SKILLS):
        count=sum(e["path"].startswith(s["id"]+"/") for e in manifest)
        lines=sum(e["lines"] for e in manifest if e["path"].startswith(s["id"]+"/"))
        panels+=f'<article role="tabpanel" id="{s["id"]}" aria-labelledby="tab-{s["id"]}" tabindex="0" {"" if i==0 else "hidden"}><header class="panel-head"><div class="eyebrow">{esc(s["full"])} · {count} original files · {lines:,} lines</div><h2>{s["thesis"]}</h2><p class="verdict">{s["summary"]}</p><p class="version">{s["version"]}</p><div class="actions"><a href="packages/{s["id"]}.zip" download>Download revised skill</a><a href="revised-skills/{s["id"]}/SKILL.md">Open revised SKILL.md</a><a href="diffs/{s["id"]}.diff">Download diff</a></div></header>'
        panels+=section("1","What the skill does",s["does"])
        panels+=section("2","How it works",s["how"])
        panels+=section("3","Gaps and source evidence",s["gaps"])
        panels+=section("4","The revised version",s["revised"])
        panels+=section("5","Blind spots worth making explicit",s["unknowns"])
        panels+=f'<section class="try"><h3>Prompt for your next run</h3><p>{esc(s["prompt"])}</p><small>Use only after choosing this local edition in your preferred harness. This task did not install or activate it.</small></section>'
        panels+=sources(s["id"])+'</article>'
    body=HTML.replace("@@TABS@@",tabs).replace("@@PANELS@@",panels).replace("@@FILES@@",str(len(manifest))).replace("@@LINES@@",f'{sum(e["lines"] for e in manifest):,}')
    (BASE/"index.html").write_text(body,encoding="utf-8")
    (BASE/"evidence/report-findings.json").write_text(json.dumps(SKILLS,indent=2),encoding="utf-8")
    print(json.dumps({"report":str(BASE/"index.html"),"tabs":len(SKILLS),"files_read":len(manifest),"lines_read":sum(e["lines"] for e in manifest),"bytes":len(body.encode("utf-8"))}))

HTML="""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark light"><meta name="referrer" content="no-referrer">
<title>JeredBlu skills · Evidence and revised editions</title>
<style>
:root{--ink:#e4eaf0;--muted:#acb8c7;--bg:#131b29;--surface:#1b2738;--line:#39485c;--accent:#8ebbe8;--warm:#f0c995;--title:#fff5e7}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:90px}body{margin:0;background:var(--bg);color:var(--ink);font-family:Calibri,'Segoe UI',sans-serif;font-size:18px;line-height:1.65}
a{color:var(--accent);text-underline-offset:4px}a:hover{color:#c5e0fc}button,input{font:inherit}a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:3px solid var(--warm);outline-offset:5px}
.mast{max-width:1160px;margin:auto;padding:58px 34px 28px}.eyebrow{font-family:Consolas,monospace;text-transform:uppercase;font-size:12px;letter-spacing:.07em;color:var(--muted)}
h1,h2{font-family:Cambria,Georgia,serif;color:var(--title);font-weight:500;line-height:1.13;letter-spacing:-.025em}h1{font-size:clamp(36px,5vw,63px);max-width:900px;margin:18px 0 24px}h2{font-size:clamp(29px,3.7vw,44px);max-width:940px;margin:16px 0}h3{font-size:25px;line-height:1.3;margin:0 0 20px;color:var(--title)}h4{font-size:20px;line-height:1.4;margin:0;color:var(--title)}p{margin:0 0 18px}li{margin:8px 0}
.lead{max-width:880px;font-size:20px}.scope{margin-top:24px;padding:18px 22px;border-left:4px solid var(--accent);background:var(--surface);font-size:16px}
.scope p:last-child{margin:0}.summary-map{margin-top:30px}.summary-map p{font-size:16px;color:var(--muted)}.map{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin-top:15px;border:1px solid var(--line);border-radius:10px;overflow:hidden}.map div{padding:16px 20px;border-right:1px solid var(--line)}.map div:last-child{border:0}.map strong{display:block;color:var(--title);font-size:17px}.map span{display:block;font-size:14px;color:var(--muted)}
.tab-shell{position:sticky;top:0;z-index:5;background:#131b29f5;border-bottom:1px solid var(--line)}.tabs{display:flex;gap:4px;overflow:auto;max-width:1160px;margin:auto;padding:10px 34px;scrollbar-width:thin}.tabs button{background:transparent;border:1px solid transparent;border-radius:6px;color:var(--muted);white-space:nowrap;padding:10px 14px;cursor:pointer;font-size:16px}.tabs button[aria-selected=true]{background:var(--surface);border-color:var(--line);color:var(--title)}
main{max-width:1160px;margin:auto;padding:36px 34px 70px}[hidden]{display:none!important}.panel-head{padding-bottom:22px}.verdict{font-size:20px;max-width:910px}.version{font:13px/1.5 Consolas,monospace;color:var(--muted)}.actions{display:flex;gap:12px;flex-wrap:wrap}.actions a{border:1px solid var(--line);padding:7px 12px;border-radius:5px;text-decoration:none;font-size:14px}
.chapter{display:grid;grid-template-columns:50px minmax(0,1fr);gap:22px;border-top:1px solid var(--line);padding:35px 0}.chapter-label{font:25px Cambria,serif;color:var(--muted)}.chapter p{max-width:950px}.flow{display:flex;gap:12px;list-style:none;margin:18px 0 28px;padding:0;flex-wrap:wrap;counter-reset:step}.flow li{counter-increment:step;flex:1 1 150px;border-top:2px solid var(--accent);font-size:15px;padding-top:12px;line-height:1.4}.flow li:before{content:counter(step) " / ";color:var(--accent);font-family:Consolas,monospace}
.table-wrap{overflow:auto;margin:22px 0;border:1px solid var(--line);border-radius:7px}table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.6}th{text-align:left;padding:14px 15px;background:var(--surface);color:var(--title);font-weight:600}td{padding:14px 15px;vertical-align:top;border-top:1px solid var(--line);min-width:110px}td:first-child{font-weight:600;color:var(--title)}.finding{padding:22px 0;border-bottom:1px dashed var(--line)}.finding:last-child{border-bottom:0}.finding-head{display:flex;align-items:baseline;gap:14px;margin-bottom:15px}.tag{color:var(--warm);border:1px solid #826b50;border-radius:4px;white-space:nowrap;font:12px/1.5 Consolas,monospace;padding:2px 7px}.evidence{font:13px/1.6 Consolas,monospace;margin:-5px 0 16px}.finding p:last-child{margin:0;color:var(--muted);font-size:16px}.calculator{background:var(--surface);padding:23px;border:1px solid var(--line);border-radius:9px}.calculator h4{margin-bottom:16px}.calculator label{display:block;font-size:16px}.calculator input{width:100%;accent-color:var(--accent)}.calc-row{display:flex;gap:26px;align-items:baseline;margin:8px 0}.calc-row strong{font:30px Cambria,serif;color:var(--warm)}.calculator p{font-size:15px;margin:0}
details{margin:18px 0;border:1px solid var(--line);border-radius:7px}summary{padding:13px 17px;cursor:pointer;color:var(--accent);font-size:16px}summary small{color:var(--muted);font-size:12px;margin-left:10px}pre{overflow:auto;padding:20px;font:13px/1.6 Consolas,monospace;background:#101724;margin:0;border-top:1px solid var(--line);white-space:pre-wrap;overflow-wrap:anywhere;tab-size:4}.source-collection{margin-top:32px}.source-file{margin:12px}.source-code{white-space:pre;max-height:650px;overflow:auto}.source-code span{display:block}.source-code b{color:#7c91ac;font-weight:400}.source-code span:target{background:#38465a;color:white}.try{padding:25px;background:var(--surface);border:1px solid var(--line);border-radius:9px;margin-top:22px}.try p{font:15px/1.7 Consolas,monospace}.try small{font-size:14px;color:var(--muted)}
.method{max-width:1160px;margin:0 auto;padding:0 34px 70px}.method h3{margin-top:24px}.method p,.method li{font-size:16px}.method details>div{padding:0 24px 20px}.footer{font:12px/1.6 Consolas,monospace;color:var(--muted);border-top:1px solid var(--line);padding:25px 0}
@media(max-width:650px){body{font-size:17px}.mast{padding:34px 20px 20px}main{padding:28px 20px 45px}.tabs{padding:9px 15px}.chapter{grid-template-columns:24px minmax(0,1fr);gap:10px;padding:26px 0}.chapter-label{font-size:20px}.finding-head{display:block}.tag{display:inline-block;margin-bottom:9px}h3{font-size:22px}.map{grid-template-columns:1fr 1fr}.map div{border-bottom:1px solid var(--line)}.method{padding:0 20px 40px}.table-wrap{margin:17px 0}.calc-row{display:block}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
@media print{body{background:white;color:black;font-size:11pt}.tabs,.actions,.calculator input,.source-collection,.edition{display:none!important}.tab-shell{display:none}article[hidden]{display:block!important}article{break-before:page}h1,h2,h3,h4,td:first-child{color:black}.chapter{break-inside:auto}.finding{break-inside:avoid}.map,.scope,.try,.calculator,th{background:#f1f3f5}.method,.mast,main{padding:20px}a{color:#224c75}}
</style></head><body>
<header class="mast"><div class="eyebrow">Local source review · 12 October 2026 · Portable editions</div>
<h1>Five skills.<br>From instructions to evidence.</h1>
<p class="lead">What each skill does, how it works, where its safeguards fall short, and a revised edition you can inspect and use. The originals remain intact.</p>
<div class="scope"><p><strong>Coverage:</strong> @@FILES@@ original files / @@LINES@@ lines read, including every skill, reference, script, changelog and test file. This downloaded directory has no Git metadata; the <a href="evidence/source-manifest.json">SHA-256 manifest</a> identifies the reviewed snapshot.</p>
<p><strong>Scope:</strong> local static source review, inert helper tests and official documentation checks. No target installation, live MCP connection, model-generation workflow or upstream publication. “Unknown unknowns” below are surfaced blind spots and hypotheses, with mitigations and remaining limits; they are not an exhaustive guarantee.</p></div>
<div class="summary-map"><div class="map"><div><strong>Instructions</strong><span>What is promised?</span></div><div><strong>Mechanism</strong><span>What is enforced?</span></div><div><strong>Evidence</strong><span>What was checked?</span></div><div><strong>Decision</strong><span>What remains uncertain?</span></div></div><p>The central distinction: a careful instruction is a policy; executable checks enforce only their specific invariants. Neither proves universal safety.</p></div>
</header>
<nav class="tab-shell" aria-label="Skill reports"><div class="tabs" role="tablist" aria-label="Choose a skill">@@TABS@@</div></nav>
<main>@@PANELS@@</main>
<aside class="method"><details><summary>Review method, validation and use of the revisions</summary><div>
<h3>What the evidence supports</h3>
<p>The original Windows regression run completed 56 tests: 50 passed and 6 failed. The revised repository suite completed 56: 53 passed and 3 legacy POSIX shell fixtures skipped. The separate portable regression suite passed 15 tests and the delegation scheduler passed 10 mocked-adapter tests. See <a href="evidence/validation.json">machine-readable validation</a>, <a href="evidence/original-windows-tests.txt">original run</a>, <a href="evidence/repo-revision-tests.txt">revised repository run</a>, <a href="evidence/revision-tests.txt">new Python tests</a>, and <a href="evidence/scheduler-tests.txt">scheduler tests</a>.</p>
<p>All five revised skill folders were checked with the skill-creator frontmatter validator. Python helpers were syntax-checked; source-file links and tabs were checked in a browser. The final browser record is <a href="evidence/browser-validation.json">browser-validation.json</a>. The <a href="evidence/independent-review.md">independent forward review</a> assesses realistic scenarios; its discovered issues were corrected and <a href="evidence/independent-recheck.md">independently rechecked</a>. These are static/inert exercises rather than a live agent-quality benchmark.</p>
<p>Browser validation covers tab/keyboard interactions, expandable evidence, link targets and desktop/mobile geometry. Pixel screenshot inspection was unavailable in this session. No claim of a screenshot-based visual review is made.</p>
<h3>How to use this package</h3>
<ol><li>Choose the skill tab, read its gaps and remaining limits, and inspect its complete revision/diff.</li><li>Download that skill’s ZIP or the <a href="packages/revised-skills.zip" download>combined revised package</a>. Each skill folder is self-contained. These are local review editions, not upstream releases.</li><li>In your harness, choose one edition of a skill to avoid duplicate names and ambiguous routing. Follow that harness’s installation interface. No global skill/configuration files were changed here.</li><li>For Windows, prefer the quoted Python commands in the revised references. Do not assume a bare bash command selects Git Bash. The macOS artifact helper remains optional and limited.</li><li>Before real use, keep the stated authorization boundary and verify any runtime/provider capability the skill depends on. A validated folder is not a certified workflow.</li></ol>
<h3>Corrections versus mitigation</h3>
<p>Scanner truncation, path separators, unsafe “safe” examples, conflicting PRD references and the workflow’s acceptance/accounting mechanics have concrete replacement code or documents. Source/deployment equivalence, OS-level sandboxing, registry pagination, hostile filesystem races, true provider budget enforcement and model-quality calibration remain explicit limits. The report does not claim those hard problems were solved by wording changes.</p>
<h3>Primary references checked for this review</h3>
<ul><li><a href="https://nodejs.org/api/vm.html">Node.js vm documentation</a>: the module is not a security mechanism for untrusted code.</li><li><a href="https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices">MCP 2025-11-25 security guidance</a> and <a href="https://modelcontextprotocol.io/specification/2025-11-25/basic/transports">transports</a>: used as a named protocol baseline; target versions need their own checks.</li><li><a href="https://docs.python.org/3/library/zipfile.html">Python ZIP documentation</a>: untrusted archive handling requires inspection and bounded extraction.</li><li><a href="https://aws.amazon.com/ses/">Amazon SES</a>: verifies the service-category correction in the PRD reference.</li></ul>
<p>Verification date: 12 October 2026. Source files and past changelog claims are distinguished from current local test outcomes. No creator-reputation or comprehensive vulnerability-corpus assessment was performed.</p>
</div></details><div class="footer">Original snapshot + revised folders + unified diffs + source hashes + offline regression evidence. No external assets or analytics are loaded by this HTML file.</div></aside>
<script>
const tabs=Array.from(document.querySelectorAll('[role=tab]'));
const panels=Array.from(document.querySelectorAll('[role=tabpanel]'));
function activate(id,focus=false,update=true){
  if(!panels.some(p=>p.id===id))return;
  tabs.forEach(t=>{const selected=t.getAttribute('aria-controls')===id;t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;if(selected&&focus)t.focus();});
  panels.forEach(p=>p.hidden=p.id!==id);
  if(update){history.replaceState(null,'','#'+id);document.querySelector('main').scrollIntoView({block:'start',behavior:'instant'});}
}
tabs.forEach((t,i)=>{t.addEventListener('click',()=>activate(t.getAttribute('aria-controls')));
  t.addEventListener('keydown',e=>{let n;if(e.key==='ArrowRight')n=(i+1)%tabs.length;else if(e.key==='ArrowLeft')n=(i-1+tabs.length)%tabs.length;else if(e.key==='Home')n=0;else if(e.key==='End')n=tabs.length-1;else return;e.preventDefault();activate(tabs[n].getAttribute('aria-controls'),true);});});
function showHash(){
  const id=decodeURIComponent(location.hash.slice(1));const target=document.getElementById(id);
  if(!target)return;const panel=target.closest('[role=tabpanel]');if(panel)activate(panel.id,false,false);
  let parent=target.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}
}
window.addEventListener('hashchange',showHash);showHash();
document.addEventListener('click',e=>{const link=e.target.closest('a.source-link');if(link){const el=document.getElementById(link.hash.slice(1));if(el){let p=el.parentElement;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement;}}}});
const range=document.getElementById('coverage');if(range)range.addEventListener('input',()=>{document.getElementById('coverage-out').textContent=range.value;document.getElementById('coverage-demo').textContent=range.value+'% weighted coverage';});
</script></body></html>"""

if __name__=="__main__":main()
