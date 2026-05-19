# Security Policy

CipherQuorum is a learning-friendly cryptography project, but security reports
should still be handled carefully.

## Reporting a Vulnerability

Please do not publish live secrets, private keys, API tokens, or exploit details
in a public issue.

For now, open a GitHub issue with a minimal description and avoid sensitive
details. A maintainer can then coordinate a safer disclosure path.

## Scope

Security-sensitive areas include:

- Shamir Secret Sharing reconstruction behavior.
- Share token parsing and validation.
- X25519 handshake and AES-GCM channel encryption.
- TCP frame parsing and size limits.
- LAN peer discovery assumptions.

## Supported Versions

CipherQuorum is currently pre-1.0. Security fixes target the latest commit on
the default branch.
