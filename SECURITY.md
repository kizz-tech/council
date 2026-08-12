# Security policy

## Supported versions

Only the latest published alpha is supported. Council executes no network
service, but its installer writes skill and advisor files into user-selected
directories, so path handling and drift protection are security-sensitive.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for this repository. Do
not open a public issue for an unpatched path traversal, overwrite, secret
exposure, or other exploitable condition.

Include the affected version, operating system, exact command, target layout,
observed result, and a minimal reproduction that contains no private data.

## Scope

Security reports are especially useful for unsafe destination resolution,
unknown-drift overwrite, archive traversal, secret inclusion, and release
integrity failures. Product-quality bugs without a security boundary can use a
normal issue.
