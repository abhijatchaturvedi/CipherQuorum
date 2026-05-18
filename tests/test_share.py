from cipherquorum.share import Share
from cipherquorum.sss import reconstruct_secret, split_secret


def test_share_token_round_trip():
    share = split_secret(b"token-secret", threshold=2, shares=3)[0]

    parsed = Share.from_token(share.to_token())

    assert parsed == share


def test_recover_from_tokens():
    shares = split_secret(b"token-secret", threshold=2, shares=3)
    parsed = [Share.from_token(share.to_token()) for share in shares[:2]]

    assert reconstruct_secret(parsed) == b"token-secret"
