from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from .discovery import browse, publish
from .share import Share
from .sss import reconstruct_secret, split_secret
from .transfer import receive_one_share, send_share


def _cmd_split_local(args: argparse.Namespace) -> int:
    shares = split_secret(args.secret.encode("utf-8"), args.threshold, args.shares)
    for share in shares:
        print(share.to_token())
    return 0


def _cmd_recover_local(args: argparse.Namespace) -> int:
    secret = reconstruct_secret(Share.from_token(token) for token in args.tokens)
    print(secret.decode("utf-8"))
    return 0


def _cmd_listen(args: argparse.Namespace) -> int:
    service = None
    try:
        if args.advertise:
            service = publish(args.name, args.port)
            print(f"advertising {args.name} on port {args.port}", file=sys.stderr)
        share = receive_one_share(args.host, args.port, timeout=args.timeout)
        Path(args.out).write_text(share.to_token() + "\n", encoding="utf-8")
        print(f"wrote share to {args.out}", file=sys.stderr)
        return 0
    finally:
        if service:
            zeroconf, info = service
            zeroconf.unregister_service(info)
            zeroconf.close()


def _cmd_split(args: argparse.Namespace) -> int:
    peers = browse(args.timeout)
    if len(peers) < args.shares:
        raise SystemExit(f"found {len(peers)} peers, need {args.shares}")

    shares = split_secret(args.secret.encode("utf-8"), args.threshold, args.shares)
    for peer, share in zip(peers[: args.shares], shares, strict=True):
        send_share(peer.host, peer.port, share)
        print(f"sent share {share.x} to {peer.name} ({peer.host}:{peer.port})", file=sys.stderr)
    return 0


def _cmd_recover(args: argparse.Namespace) -> int:
    service = publish(args.name, args.port)
    tokens: list[str] = []
    try:
        deadline = time.monotonic() + args.timeout
        while len(tokens) < args.threshold:
            remaining = max(0.1, deadline - time.monotonic())
            share = receive_one_share(args.host, args.port, timeout=remaining)
            tokens.append(share.to_token())
            print(f"received share {share.x}", file=sys.stderr)
        secret = reconstruct_secret(Share.from_token(token) for token in tokens)
        print(secret.decode("utf-8"))
        return 0
    finally:
        zeroconf, info = service
        zeroconf.unregister_service(info)
        zeroconf.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cipherquorum")
    sub = parser.add_subparsers(dest="command", required=True)

    split_local = sub.add_parser("split-local", help="split a secret and print share tokens")
    split_local.add_argument("--secret", required=True)
    split_local.add_argument("--threshold", type=int, required=True)
    split_local.add_argument("--shares", type=int, required=True)
    split_local.set_defaults(func=_cmd_split_local)

    recover_local = sub.add_parser("recover-local", help="recover a secret from share tokens")
    recover_local.add_argument("tokens", nargs="+")
    recover_local.set_defaults(func=_cmd_recover_local)

    listen = sub.add_parser("listen", help="receive one encrypted share over TCP")
    listen.add_argument("--name", default="peer")
    listen.add_argument("--host", default="0.0.0.0")
    listen.add_argument("--port", type=int, default=8765)
    listen.add_argument("--out", default="cipherquorum.share")
    listen.add_argument("--timeout", type=float, default=None)
    listen.add_argument("--advertise", action=argparse.BooleanOptionalAction, default=True)
    listen.set_defaults(func=_cmd_listen)

    split = sub.add_parser("split", help="discover peers and send encrypted shares")
    split.add_argument("--secret", required=True)
    split.add_argument("--threshold", type=int, required=True)
    split.add_argument("--shares", type=int, required=True)
    split.add_argument("--timeout", type=float, default=8.0)
    split.set_defaults(func=_cmd_split)

    recover = sub.add_parser("recover", help="collect threshold shares over the LAN")
    recover.add_argument("--name", default="recovery")
    recover.add_argument("--host", default="0.0.0.0")
    recover.add_argument("--port", type=int, default=8765)
    recover.add_argument("--threshold", type=int, required=True)
    recover.add_argument("--timeout", type=float, default=60.0)
    recover.set_defaults(func=_cmd_recover)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
