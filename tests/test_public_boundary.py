from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".pdf", ".png", ".pt", ".pth", ".ckpt", ".pyc"}
FORBIDDEN_PARTS = {".pytest_cache", "__pycache__", "data"}
FORBIDDEN_TEXT = (
    "/Users/" "chenmao/",
    "takumi." "corp.kuaishou.com",
    "DEEPSEEK_" "API_KEY=",
    "s" "k-",
)
REQUIRED_FILES = {
    "questions/q1-why-deep-networks-fail.md",
    "questions/q2-why-attention-works.md",
    "questions/q3-why-diffusion-generates.md",
    "code/resnet/plain_vs_residual.py",
    "code/transformer/tiny_attention.py",
    "code/ddpm/simple_ddpm.py",
}


def public_files():
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / path for path in result.stdout.decode().split("\0") if path]


def artifact_violations(root, files):
    violations = []
    for path in files:
        relative = path.relative_to(root)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or FORBIDDEN_PARTS.intersection(relative.parts):
            violations.append(str(relative))
        if path.name == "input.txt":
            violations.append(str(relative))
    return violations


def test_public_tree_excludes_private_or_generated_artifacts():
    assert artifact_violations(ROOT, public_files()) == []


def test_public_tree_excludes_generated_png_artifacts(tmp_path):
    artifact = tmp_path / "code" / "resnet" / "output.png"
    artifact.parent.mkdir(parents=True)
    artifact.write_bytes(b"generated plot")

    assert artifact_violations(tmp_path, [artifact]) == ["code/resnet/output.png"]


def test_generated_png_artifacts_are_ignored_by_git():
    result = subprocess.run(
        ["git", "check-ignore", "-q", "code/resnet/output.png"],
        cwd=ROOT,
    )

    assert result.returncode == 0


def test_required_learning_material_is_present():
    present = {str(path.relative_to(ROOT)) for path in public_files()}
    assert REQUIRED_FILES <= present


def test_text_files_do_not_expose_local_or_company_data():
    violations = []
    for path in public_files():
        if path.suffix.lower() not in {".md", ".py", ".toml", ".yml", ".yaml", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN_TEXT:
            if needle in text:
                violations.append(f"{path.relative_to(ROOT)}: {needle}")
    assert violations == []
