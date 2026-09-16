from pathlib import Path

from scripts.fetch_papers import load_catalog


def test_catalog_contains_the_three_reviewed_papers():
    papers = load_catalog(Path("papers.yml"))

    assert [paper.slug for paper in papers] == ["resnet", "transformer", "ddpm"]
    assert [paper.version for paper in papers] == ["v1", "v7", "v2"]
    for paper in papers:
        assert paper.abstract_url.startswith("https://arxiv.org/abs/")
        assert paper.pdf_url.startswith("https://arxiv.org/pdf/")
        assert len(paper.sha256) == 64
        assert paper.sha256 == paper.sha256.lower()
        assert set(paper.sha256) <= set("0123456789abcdef")
