from __future__ import annotations

import socket
import time
from dataclasses import dataclass

SERVICE_TYPE = "_cipherquorum._tcp.local."


@dataclass(frozen=True)
class Peer:
    name: str
    host: str
    port: int


def publish(name: str, port: int):
    try:
        from zeroconf import ServiceInfo, Zeroconf
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("zeroconf is required for LAN discovery") from exc

    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    zeroconf = Zeroconf()
    info = ServiceInfo(
        SERVICE_TYPE,
        f"{name}.{SERVICE_TYPE}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={"app": "cipherquorum"},
        server=f"{hostname}.local.",
    )
    zeroconf.register_service(info)
    return zeroconf, info


def browse(timeout: float = 8.0) -> list[Peer]:
    try:
        from zeroconf import ServiceBrowser, ServiceListener, Zeroconf
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("zeroconf is required for LAN discovery") from exc

    peers: dict[str, Peer] = {}

    class Listener(ServiceListener):
        def add_service(self, zeroconf, service_type, name):
            info = zeroconf.get_service_info(service_type, name)
            if not info or not info.addresses:
                return
            host = socket.inet_ntoa(info.addresses[0])
            peers[name] = Peer(name=name.removesuffix("." + SERVICE_TYPE), host=host, port=info.port)

        def update_service(self, zeroconf, service_type, name):
            self.add_service(zeroconf, service_type, name)

        def remove_service(self, zeroconf, service_type, name):
            peers.pop(name, None)

    zeroconf = Zeroconf()
    try:
        ServiceBrowser(zeroconf, SERVICE_TYPE, Listener())
        time.sleep(timeout)
        return list(peers.values())
    finally:
        zeroconf.close()
