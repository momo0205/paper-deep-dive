import hashlib

import pytest

from scripts.fetch_papers import HashMismatch, Paper, download_paper


def make_paper(sha256: str) -> Paper:
    return Paper(
        slug="resnet",
        title="ResNet",
        authors=("Kaiming He",),
        arxiv_id="1512.03385",
        version="v1",
        abstract_url="https://arxiv.org/abs/1512.03385v1",
        pdf_url="https://arxiv.org/pdf/1512.03385v1",
        sha256=sha256,
    )


def test_download_writes_verified_pdf_atomically(tmp_path):
    contents = b"official-paper-bytes"
    paper = make_paper(hashlib.sha256(contents).hexdigest())

    result = download_paper(paper, tmp_path, opener=lambda _: contents)

    assert result == tmp_path / "resnet-1512.03385v1.pdf"
    assert result.read_bytes() == contents
    assert list(tmp_path.iterdir()) == [result]


def test_download_rejects_hash_mismatch(tmp_path):
    paper = make_paper("0" * 64)

    with pytest.raises(HashMismatch):
        download_paper(paper, tmp_path, opener=lambda _: b"not-the-paper")

    assert list(tmp_path.iterdir()) == []
