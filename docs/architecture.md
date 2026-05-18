# CipherQuorum Architecture

CipherQuorum has four boundaries:

1. `sss.py` implements finite-field arithmetic, split, and reconstruct.
2. `share.py` converts share objects to URL-safe tokens and back.
3. `channel.py` creates an encrypted session for a connected socket.
4. `discovery.py` and `transfer.py` handle LAN service discovery and framed delivery.

## Secret Sharing

Each byte of the secret is treated as the constant term of a random polynomial over
GF(256). The threshold is the polynomial degree plus one. A share contains one
evaluation point per secret byte.

The implementation stores a SHA-256 digest in each share so recovery can reject
wrong combinations. The digest is not a substitute for access control; it only
prevents returning corrupted plaintext.

## Encrypted Channel

Peers exchange ephemeral X25519 public keys, derive a shared key with HKDF-SHA256,
and encrypt every framed payload with AES-GCM. Nonces are random 96-bit values.

## Discovery

Peers publish `_cipherquorum._tcp.local.` records through Zeroconf. The sender waits
for enough peers, then opens direct TCP sockets. Discovery is only for finding peers;
all payloads still travel through encrypted direct channels.
