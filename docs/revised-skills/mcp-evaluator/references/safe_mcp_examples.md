# Mitigation evidence, with limits
Use scripts/boundaries.py for tested Python containment and positive-integer parsing.
The resolved candidate must be a child of the resolved root, not a string prefix.
That rejects sibling-prefix traversal and resolved symlink escape in a stable tree;
it does not close concurrent filesystem races. Use OS-enforced isolation/handles
where hostile writers can mutate the tree.
HTTPS origin allowlisting alone does not constrain redirects or DNS rebinding.
Node.js vm is NOT a security sandbox:
https://nodejs.org/api/vm.html
cwd, timeout and captured output are also not subprocess containment.
Hashing a predictable username is pseudonymization, not proof of anonymity.
Opt-in telemetry still needs payload/retention/recipient analysis.
Secret redaction must cover nested values, headers and error paths, or avoid payload logs.
Python Fernet.generate_key() returns bytes: decode once for keyring storage; supply
bytes to Fernet. Test both new-key and existing-key paths before claiming correctness.
Retry wrappers cannot safely repeat payments, messages or writes without idempotency.
TypeScript annotations do not validate environment values: reject NaN, infinity,
partial numeric strings, negative/zero values and unreasonable bounds at runtime.
