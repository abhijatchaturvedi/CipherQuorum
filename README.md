# CipherQuorum

> Threshold secret sharing for teams that want local-first recovery without a
> central server.

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-0f766e.svg)](LICENSE)
[![Crypto](https://img.shields.io/badge/crypto-Shamir%20SSS%20%2B%20AES--GCM-7c3aed)](docs/architecture.md)

CipherQuorum splits sensitive values into threshold shares and moves those
shares directly between peers on the same LAN. Any `K` of `N` shares can recover
the original secret; fewer than `K` reveal nothing useful.

```text
secret -> split into N shares -> distribute over encrypted LAN channels
                                      |
                         any K shares recover the secret
```

## Highlights

- **Threshold recovery:** Shamir Secret Sharing over GF(256).
- **No central server:** peers discover each other with Zeroconf/mDNS.
- **Encrypted transfer:** X25519 key exchange with AES-256-GCM payloads.
- **CLI-first workflow:** simple `split`, `listen`, and `recover` commands.
- **Offline mode:** local share generation and recovery for demos and tests.
- **Contributor-friendly:** small modules, focused tests, and architecture docs.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
```

Using `uv`:

```powershell
uv sync --extra dev
```

## Quick Demo

Create five shares where any three can recover the secret:

```powershell
cipherquorum split-local --secret "prod-db-password" --threshold 3 --shares 5
```

Recover from any three returned share tokens:

```powershell
cipherquorum recover-local SHARE_1 SHARE_2 SHARE_3
```

You can also use the short command alias:

```powershell
cq split-local --secret "api-key" --threshold 2 --shares 3
```

## LAN Workflow

On receiver machines:

```powershell
cipherquorum listen --name alice --port 8765 --out alice.share
```

On the sender:

```powershell
cipherquorum split --secret "prod-db-password" --threshold 2 --shares 3
```

The sender discovers peers advertising `_cipherquorum._tcp.local.`, opens direct TCP
connections, performs an X25519 handshake, and sends each peer one encrypted share.

## Commands

| Command | Purpose |
| --- | --- |
| `cipherquorum split-local` | Print share tokens for offline use. |
| `cipherquorum recover-local` | Recover a secret from share tokens. |
| `cipherquorum listen` | Advertise a peer and receive one encrypted share. |
| `cipherquorum split` | Discover peers and send encrypted shares. |
| `cipherquorum recover` | Collect threshold shares over the LAN and recover. |

## Project Layout

```text
src/cipherquorum/
  cli.py          command-line interface
  sss.py          Shamir Secret Sharing over GF(256)
  channel.py      encrypted socket channel
  discovery.py    Zeroconf service publishing and browsing
  transfer.py     length-prefixed peer transfer helpers
  share.py        share serialization
tests/
  test_sss.py
  test_share.py
docs/
  architecture.md
```

## Design

CipherQuorum never reconstructs a secret unless the caller provides at least the
configured threshold of valid shares. Fewer shares are useless for reconstruction.
The LAN path requires `cryptography` and `zeroconf`.

Read the deeper design notes in [docs/architecture.md](docs/architecture.md).

## Contributing

Contributions are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md), then run:

```powershell
uv run --extra dev pytest
uv run --extra dev ruff check .
```

Please also read the [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

## License

CipherQuorum is released under the [MIT License](LICENSE).
