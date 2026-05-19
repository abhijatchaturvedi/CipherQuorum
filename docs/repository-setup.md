# Repository Setup Checklist

Use this checklist after pushing the repository to GitHub.

## Visibility

- Set repository visibility to **Public**.
- Add a concise About description:

```text
Shamir Secret Sharing CLI for encrypted, local-first secret recovery over LAN.
```

## Topics

Add these GitHub topics:

```text
python
cryptography
shamir-secret-sharing
secret-sharing
threshold-cryptography
cybersecurity
cli
p2p
mdns
zeroconf
aes-gcm
x25519
local-first
secret-management
lan
```

## Social Preview

Use a clean terminal screenshot showing:

```powershell
cq split-local --secret "api-key" --threshold 2 --shares 3
cq recover-local SHARE_1 SHARE_2
```

## Collaboration

- Enable Issues.
- Enable Discussions if you want design questions and roadmap discussion.
- Keep branch protection lightweight until contributors arrive.
- Require CI before merging once the first pull request is opened.
