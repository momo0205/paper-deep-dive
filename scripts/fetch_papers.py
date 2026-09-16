"""Download the reviewed arXiv paper versions with integrity verification."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator
from urllib.request import urlopen

import yaml


@dataclass(frozen=True)
class Paper:
    slug: str
    title: str
    authors: tuple[str, ...]
    arxiv_id: str
    version: str
    abstract_url: str
    pdf_url: str
    sha256: str


class HashMismatch(ValueError):
    """Raised when a downloaded paper differs from its reviewed source."""


def load_catalog(path: Path) -> list[Paper]:
    """Load the version-pinned paper records from a YAML catalog."""
    catalog = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [
        Paper(
            slug=record["slug"],
            title=record["title"],
            authors=tuple(record["authors"]),
            arxiv_id=record["arxiv_id"],
            version=record["version"],
            abstract_url=record["abstract_url"],
            pdf_url=record["pdf_url"],
            sha256=record["sha256"],
        )
        for record in catalog["papers"]
    ]


def _read_chunks(response: object) -> Iterator[bytes]:
    if isinstance(response, bytes):
        yield response
        return

    with response:  # type: ignore[union-attr]
        while chunk := response.read(64 * 1024):  # type: ignore[union-attr]
            yield chunk


def download_paper(paper: Paper, destination: Path, opener: Callable = urlopen) -> Path:
    """Download one paper atomically, rejecting content with the wrong digest."""
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / f"{paper.slug}-{paper.arxiv_id}{paper.version}.pdf"
    digest = hashlib.sha256()
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination, prefix=f".{paper.slug}-", suffix=".part", delete=False
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            for chunk in _read_chunks(opener(paper.pdf_url)):
                digest.update(chunk)
                temporary_file.write(chunk)

        actual_digest = digest.hexdigest()
        if not hmac.compare_digest(actual_digest, paper.sha256):
            raise HashMismatch(
                f"SHA-256 mismatch for {paper.slug}: expected {paper.sha256}, got {actual_digest}"
            )

        return temporary_path.replace(target)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="*", help="paper slugs to download; defaults to all papers")
    parser.add_argument("--output-dir", type=Path, default=Path("papers"))
    arguments = parser.parse_args()

    catalog_path = Path(__file__).resolve().parents[1] / "papers.yml"
    papers = load_catalog(catalog_path)
    papers_by_slug = {paper.slug: paper for paper in papers}
    requested_slugs = arguments.slugs or list(papers_by_slug)

    for slug in requested_slugs:
        if slug not in papers_by_slug:
            parser.error(f"unknown paper slug: {slug}")
        downloaded = download_paper(papers_by_slug[slug], arguments.output_dir)
        print(downloaded)


if __name__ == "__main__":
    main()
