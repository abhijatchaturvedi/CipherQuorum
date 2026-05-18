from __future__ import annotations

import os
import socket

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import x25519
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
except ImportError:  # pragma: no cover - exercised only without optional dependency
    hashes = serialization = x25519 = AESGCM = HKDF = None

from .transfer import recv_frame, send_frame


class SecureChannel:
    def __init__(self, sock: socket.socket, key: bytes):
        self._sock = sock
        self._aead = AESGCM(key)

    @classmethod
    def connect(cls, sock: socket.socket) -> "SecureChannel":
        return cls._handshake(sock, initiator=True)

    @classmethod
    def accept(cls, sock: socket.socket) -> "SecureChannel":
        return cls._handshake(sock, initiator=False)

    @classmethod
    def _handshake(cls, sock: socket.socket, initiator: bool) -> "SecureChannel":
        if x25519 is None:
            raise RuntimeError("cryptography is required for encrypted channels")

        private_key = x25519.X25519PrivateKey.generate()
        public_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

        if initiator:
            send_frame(sock, public_bytes)
            peer_bytes = recv_frame(sock)
        else:
            peer_bytes = recv_frame(sock)
            send_frame(sock, public_bytes)

        peer_key = x25519.X25519PublicKey.from_public_bytes(peer_bytes)
        shared = private_key.exchange(peer_key)
        key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"cipherquorum-v1-channel",
        ).derive(shared)
        return cls(sock, key)

    def send(self, plaintext: bytes) -> None:
        nonce = os.urandom(12)
        send_frame(self._sock, nonce + self._aead.encrypt(nonce, plaintext, None))

    def recv(self) -> bytes:
        payload = recv_frame(self._sock)
        if len(payload) < 13:
            raise ValueError("encrypted frame is too short")
        return self._aead.decrypt(payload[:12], payload[12:], None)
