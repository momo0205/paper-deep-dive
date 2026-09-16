from pathlib import Path
import os
import subprocess
import sys

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


def test_public_documentation_links_pinned_sources_and_offline_validation():
    """Guard the clone-to-study contract against an incomplete public README."""
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    learning_loop_start = readme.index("## 6–9 周学习循环")
    assert readme.index("为什么网络越深越难训练") < learning_loop_start
    assert readme.index("为什么注意力能替代序列建模") < learning_loop_start
    assert readme.index("为什么扩散模型能生成高质量样本") < learning_loop_start
    assert "https://arxiv.org/abs/1512.03385v1" in readme
    assert "https://arxiv.org/abs/1706.03762v7" in readme
    assert "https://arxiv.org/abs/2006.11239v2" in readme
    assert "PDF" in readme
    assert "不再分发" in readme
    assert "官方获取" in readme
    assert "SHA-256" in readme
    assert "python -m venv" in readme
    assert "pip install -e ." in readme
    assert "pytest -q" in readme
    for script in (
        "code/resnet/plain_vs_residual.py",
        "code/transformer/tiny_attention.py",
        "code/ddpm/simple_ddpm.py",
    ):
        assert f"python {script} --smoke --offline" in readme


def test_license_limits_mit_to_original_repository_content():
    """Guard against claiming ownership of the linked papers or datasets."""
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")

    assert "原创代码、文档与组织内容" in license_text
    assert "论文" in license_text
    assert "数据集" in license_text
    assert "不覆盖、也不授予" in license_text
    assert "不归本仓库所有" in license_text


def test_editable_install_exposes_paper_fetcher_outside_repository(tmp_path):
    """Guard against root-directory imports masking a broken editable artifact."""
    environment = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from scripts.fetch_papers import load_catalog; print(load_catalog.__name__)",
        ],
        cwd=tmp_path,
        env=environment,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "load_catalog"


def test_ci_runs_python_311_pytest_and_all_offline_smokes():
    """Guard the public CI contract against silently shrinking validation."""
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "actions/checkout@v4" in workflow
    assert "actions/setup-python@v5" in workflow
    assert 'python-version: "3.11"' in workflow
    assert "- run: pytest -q" in workflow
    for script in (
        "code/resnet/plain_vs_residual.py",
        "code/transformer/tiny_attention.py",
        "code/ddpm/simple_ddpm.py",
    ):
        assert f"python {script} --smoke --offline" in workflow


def test_reproducibility_docs_limit_output_directory_guarantee_to_explicit_commands():
    """Keep default teaching-script output behavior distinct from CI guarantees."""
    reproducibility = (ROOT / "docs/reproducibility.md").read_text(encoding="utf-8")

    assert "README/CI 命令显式传入 `--output-dir`" in reproducibility
    assert "默认教学行为" in reproducibility


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
