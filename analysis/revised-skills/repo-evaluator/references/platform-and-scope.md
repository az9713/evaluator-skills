# Platform and evidence scope
Python 3.11+ is recommended for TOML. Use Python 3.9+ only with explicit TOML gaps.
PowerShell: python -I "C:\path with spaces\repo-evaluator\scripts\scan.py" "C:\target" --json
macOS/Linux: python3 -I "/path/repo-evaluator/scripts/scan.py" "/target" --json
Use scripts/fetch.py for public GitHub acquisition; it prints a JSON checkout receipt.
scan.py and deps.py use slash-normalized repository-relative evidence paths and explicit UTF-8.
Run: python -B -m unittest discover -s "/path/repo-evaluator/tests" -v
Three legacy POSIX shell fixtures are skipped on Windows, not counted as passed.
The independent package tests exercise the new Python fetch and archive helpers.

gh auth is optional for a bounded offline/local-source review. If unavailable, label
provenance and incident research unknown; use accessible official APIs/connectors if available.
Never request credentials just to inspect local source. Do not print gh auth tokens.
A locally downloaded directory with no .git has file hashes, not a verified commit.
The existing score.py requires a verified full commit. Do not fabricate one; deliver
an unscored evidence assessment for that scope until a revision is corroborated.

Review release workflow permissions, action pins, publish identity and install receipts.
A signature attests identity/integrity under its trust model, not absence of malicious code.
Literal host inventories omit constructed URLs, native sockets, IPv6 and dependency behavior.
Unsupported locks and build flags require a separate review; known-advisory absence
does not rule out a new or unpublished vulnerability.
Source review and deployed service behavior are different scopes. Repeat review when
code, tool descriptions, dependency pins, privileges, ownership or deployment changes.
Metadata helpers fetch limited pages; compute contributor shares only for that sample.
Do not infer organic stars or a safety threshold from fork/star ratios.
Registry metadata is a linkage clue; independently compare the exact package version.

Optional inspect_artifact.sh remains a macOS-oriented sampled helper, not a complete
artifact audit. Whitespace/newline paths, parser failures and sampled omissions require
manual review in an isolated environment. Do not give signature/artifact passes solely
from its exit code. A native Windows Authenticode check is not supplied here.
safe_archive.py is the portable ZIP/TAR helper; it refuses links and special entries.
Parsers are not sandboxes. Hostile artifacts belong in a disposable environment.


Scanner JSON preserves category/file/line but omits raw matching lines to avoid
printing embedded credentials. Credential-bearing filenames are skipped, explicitly
making scope incomplete. Linked/reparse roots and ancestors are refused; junction
directories are skipped as incomplete. deps.py follows the same directory boundary.
    Dependency output omits raw install-script/source/unresolved-requirement values;
    package names/versions remain visible and can be private. Use offline mode and
    privately inspect/redact metadata before sharing it. Review omitted values locally.
