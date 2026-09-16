import hashlib
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _repository_snapshot():
    """Capture user-facing files while ignoring test/interpreter bookkeeping."""
    snapshot = {}
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in {".git", ".venv", ".pytest_cache", "__pycache__"}
               for part in relative.parts):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        snapshot[relative] = digest
    return snapshot


@pytest.mark.parametrize(
    ("script", "marker"),
    [
        ("code/resnet/plain_vs_residual.py", "residual/plain"),
        ("code/transformer/tiny_attention.py", "attention shape"),
        ("code/ddpm/simple_ddpm.py", "sample shape"),
    ],
)
def test_offline_smoke_command(script, marker, tmp_path):
    before = _repository_snapshot()
    result = subprocess.run(
        [
            sys.executable,
            script,
            "--smoke",
            "--offline",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=90,
    )
    after = _repository_snapshot()

    assert result.returncode == 0, result.stderr
    assert marker in result.stdout
    assert after == before, "smoke command modified files outside --output-dir"
