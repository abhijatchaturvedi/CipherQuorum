import pytest

from cipherquorum.sss import reconstruct_secret, split_secret


def test_reconstructs_from_threshold_subset():
    shares = split_secret(b"correct horse battery staple", threshold=3, shares=5)

    assert reconstruct_secret([shares[0], shares[2], shares[4]]) == b"correct horse battery staple"


def test_rejects_too_few_shares():
    shares = split_secret(b"secret", threshold=3, shares=5)

    with pytest.raises(ValueError, match="need at least 3 shares"):
        reconstruct_secret(shares[:2])


def test_rejects_duplicate_share_index():
    shares = split_secret(b"secret", threshold=2, shares=3)

    with pytest.raises(ValueError, match="duplicate"):
        reconstruct_secret([shares[0], shares[0]])


def test_threshold_one_behaves_like_direct_recovery():
    shares = split_secret(b"solo", threshold=1, shares=3)

    assert reconstruct_secret([shares[1]]) == b"solo"
