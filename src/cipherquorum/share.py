from __future__ import annotations

import base64
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Share:
    x: int
    y: bytes
    threshold: int
    total: int
    digest: str

    def to_token(self) -> str:
        payload = {
            "v": 1,
            "x": self.x,
            "y": base64.urlsafe_b64encode(self.y).decode("ascii"),
            "threshold": self.threshold,
            "total": self.total,
            "digest": self.digest,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")

    @classmethod
    def from_token(cls, token: str) -> "Share":
        padded = token + "=" * (-len(token) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
        if payload.get("v") != 1:
            raise ValueError("unsupported share token version")
        return cls(
            x=int(payload["x"]),
            y=base64.urlsafe_b64decode(payload["y"].encode("ascii")),
            threshold=int(payload["threshold"]),
            total=int(payload["total"]),
            digest=str(payload["digest"]),
        )
