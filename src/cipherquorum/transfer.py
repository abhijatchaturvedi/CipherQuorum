from __future__ import annotations

import socket
import struct

from .share import Share

MAX_FRAME = 4 * 1024 * 1024


def send_frame(sock: socket.socket, payload: bytes) -> None:
    sock.sendall(struct.pack("!I", len(payload)))
    sock.sendall(payload)


def recv_frame(sock: socket.socket) -> bytes:
    header = _recv_exact(sock, 4)
    size = struct.unpack("!I", header)[0]
    if size > MAX_FRAME:
        raise ValueError("frame exceeds maximum size")
    return _recv_exact(sock, size)


def _recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise ConnectionError("connection closed while reading frame")
        chunks.extend(chunk)
    return bytes(chunks)


def send_share(host: str, port: int, share: Share, timeout: float = 10.0) -> None:
    from .channel import SecureChannel

    with socket.create_connection((host, port), timeout=timeout) as sock:
        channel = SecureChannel.connect(sock)
        channel.send(share.to_token().encode("ascii"))


def receive_one_share(host: str, port: int, timeout: float | None = None) -> Share:
    from .channel import SecureChannel

    with socket.create_server((host, port), reuse_port=False) as server:
        server.settimeout(timeout)
        conn, _ = server.accept()
        with conn:
            channel = SecureChannel.accept(conn)
            return Share.from_token(channel.recv().decode("ascii"))
