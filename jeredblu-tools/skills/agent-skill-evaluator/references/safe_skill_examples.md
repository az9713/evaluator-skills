# Conditions that must be established
A reviewed subprocess is not sandboxed by cwd, timeout or capture_output.
A user-provided path may still escape scope: resolve/canonicalize and compare path
components; reject symlinks/reparse points when the access policy forbids them.
A prefix check, file existence check or familiar library is insufficient.
Network reads disclose IP/metadata even when no document payload is uploaded.
Safe behavior requires purpose, authorized scope, enforced boundary and evidence.
Do not run a target helper to prove it safe; analyze its code as data.
