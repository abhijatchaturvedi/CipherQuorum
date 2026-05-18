from __future__ import annotations

import hashlib
import secrets
from collections.abc import Iterable

from .share import Share

AES_POLY = 0x11B


def gf_add(a: int, b: int) -> int:
    return a ^ b


def gf_mul(a: int, b: int) -> int:
    result = 0
    while b:
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 0x100:
            a ^= AES_POLY
    return result & 0xFF


def gf_pow(a: int, power: int) -> int:
    result = 1
    while power:
        if power & 1:
            result = gf_mul(result, a)
        a = gf_mul(a, a)
        power >>= 1
    return result


def gf_inv(a: int) -> int:
    if a == 0:
        raise ZeroDivisionError("zero has no multiplicative inverse in GF(256)")
    return gf_pow(a, 254)


def gf_div(a: int, b: int) -> int:
    return gf_mul(a, gf_inv(b))


def _eval_poly(coefficients: list[int], x: int) -> int:
    value = 0
    for coefficient in reversed(coefficients):
        value = gf_mul(value, x)
        value = gf_add(value, coefficient)
    return value


def split_secret(secret: bytes, threshold: int, shares: int) -> list[Share]:
    if not secret:
        raise ValueError("secret must not be empty")
    if threshold < 1:
        raise ValueError("threshold must be at least 1")
    if shares < threshold:
        raise ValueError("shares must be greater than or equal to threshold")
    if shares > 255:
        raise ValueError("shares cannot exceed 255 in GF(256)")

    digest = hashlib.sha256(secret).hexdigest()
    ys = [bytearray() for _ in range(shares)]

    for byte in secret:
        coefficients = [byte] + [secrets.randbelow(256) for _ in range(threshold - 1)]
        for index in range(1, shares + 1):
            ys[index - 1].append(_eval_poly(coefficients, index))

    return [
        Share(x=index, y=bytes(ys[index - 1]), threshold=threshold, total=shares, digest=digest)
        for index in range(1, shares + 1)
    ]


def reconstruct_secret(shares: Iterable[Share]) -> bytes:
    selected = list(shares)
    if not selected:
        raise ValueError("at least one share is required")

    threshold = selected[0].threshold
    digest = selected[0].digest
    y_length = len(selected[0].y)

    if len(selected) < threshold:
        raise ValueError(f"need at least {threshold} shares")
    if len({share.x for share in selected}) != len(selected):
        raise ValueError("duplicate share index")
    if any(share.threshold != threshold or share.digest != digest for share in selected):
        raise ValueError("shares do not belong to the same secret")
    if any(len(share.y) != y_length for share in selected):
        raise ValueError("shares have inconsistent payload lengths")

    points = selected[:threshold]
    recovered = bytearray()

    for byte_index in range(y_length):
        value = 0
        for point in points:
            numerator = 1
            denominator = 1
            for other in points:
                if point.x == other.x:
                    continue
                numerator = gf_mul(numerator, other.x)
                denominator = gf_mul(denominator, gf_add(point.x, other.x))
            value ^= gf_mul(point.y[byte_index], gf_div(numerator, denominator))
        recovered.append(value)

    secret = bytes(recovered)
    if hashlib.sha256(secret).hexdigest() != digest:
        raise ValueError("share set failed integrity check")
    return secret
