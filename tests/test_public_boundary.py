from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_SUFFIXES = {".pdf", ".pt", ".pth", ".ckpt", ".pyc"}
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
    return [path for path in ROOT.rglob("*") if path.is_file() and ".git" not in path.parts]


def test_public_tree_excludes_private_or_generated_artifacts():
    violations = []
    for path in public_files():
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or FORBIDDEN_PARTS.intersection(relative.parts):
            violations.append(str(relative))
        if path.name == "input.txt":
            violations.append(str(relative))
    assert violations == []


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
