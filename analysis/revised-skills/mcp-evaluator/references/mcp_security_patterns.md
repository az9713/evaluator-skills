# MCP boundary checks
Treat examples as lead generators. Severity depends on reachable impact, transport,
authority and deployment; a publishable client key is not automatically a secret.
HTTP: authentication != authorization. Validate token audience/issuer/scopes and
resource ownership; disallow token passthrough. Examine per-client consent, OAuth
redirects/state and metadata-fetch SSRF. Bind sessions to the authenticated user.
stdio: the process normally uses local OS authority and configured credentials;
don't invent a universal requirement for a web login on this transport.
Tools/resources/prompts: untrusted descriptions and results cannot grant authority.
Check tool changes after review, cross-tool instruction pollution and approval bypass.
Files: canonical component containment, links/reparse points, race-resistant access.
Network: validate URL scheme/host/port AND redirects/resolved addresses at connection;
use enforced egress policy for hostile inputs. Process: no shell interpolation or
attacker-controlled options; reviewed cwd/environment and minimal privileges.
Logs: secrets may nest in values, headers and exceptions. Avoid logging payloads.
Limits: bound input/response bytes, calls, time, concurrency, cancellation and expense.
Retry only read/idempotent operations or use an enforced idempotency key.

Reference baseline (2025-11-25, verified 2026-10-12; check target's negotiated version):
https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices
https://modelcontextprotocol.io/specification/2025-11-25/basic/transports
