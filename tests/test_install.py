import importlib.util
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_installer_dry_run_is_read_only(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "install.py"), "--agents", "all", "--dry-run", "--no-mcp"], capture_output=True, text=True)
    assert result.returncode == 0
    plan = json.loads(result.stdout)
    assert set(plan["skill_paths"]) == {"codex", "claude", "opencode", "pi"}


def test_uninstall_rejects_unowned_manifest(tmp_path):
    uninstall = load_script("uninstall")
    (tmp_path / "install-manifest.json").write_text('{"owner":"someone-else"}', encoding="utf-8")
    try:
        uninstall.plan_uninstall(tmp_path, all_items=True)
        assert False
    except RuntimeError:
        pass


def test_launchers_quote_paths_with_spaces():
    install = load_script("install")
    posix = install.launcher_content(PurePosixPath("/tmp/Laya 测试/python"), windows=False)
    assert "'/tmp/Laya 测试/python'" in posix
    windows = install.launcher_content(PureWindowsPath(r"C:\Users\Test User\laya-router\python.exe"), windows=True)
    assert '"C:\\Users\\Test User\\laya-router\\python.exe"' in windows


def test_uninstall_symlink_uses_canonical_target(tmp_path, monkeypatch):
    uninstall = load_script("uninstall")
    base = tmp_path / "data"
    base.mkdir()
    source = base / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("test", encoding="utf-8")
    target = tmp_path / "skills" / "laya-router"
    target.parent.mkdir()
    target.symlink_to(source, target_is_directory=True)
    alias = tmp_path / "alias"
    alias.symlink_to(base, target_is_directory=True)
    manifest = {"owner": "laya-router-skill", "paths": [str(source)],
                "skills": {str(target): {"mode": "symlink", "source": str(alias / "skill"), "agents": ["claude"]}},
                "mcp": {}, "launchers": {}}
    (base / "install-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(uninstall, "data_dir", lambda: base)
    assert uninstall.main(["--all"]) == 0
    assert not target.is_symlink()


def test_uninstall_preserves_modified_skill_and_runtime(tmp_path, monkeypatch):
    install = load_script("install")
    uninstall = load_script("uninstall")
    base = tmp_path / "data"
    base.mkdir()
    source = base / "skill"
    source.mkdir()
    (source / "SKILL.md").write_text("original", encoding="utf-8")
    target = tmp_path / "agent" / "laya-router"
    target.mkdir(parents=True)
    file = target / "SKILL.md"
    file.write_text("original", encoding="utf-8")
    original_hash = install.tree_digest(target)
    file.write_text("user edit", encoding="utf-8")
    manifest = {"owner": "laya-router-skill", "paths": [str(source)],
                "skills": {str(target): {"mode": "copy", "source": str(source), "agents": ["claude"], "sha256": original_hash}},
                "mcp": {}, "launchers": {}}
    (base / "install-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(uninstall, "data_dir", lambda: base)
    assert uninstall.main(["--all"]) == 0
    assert file.read_text(encoding="utf-8") == "user edit"
    assert source.exists()
    assert str(target) in json.loads((base / "install-manifest.json").read_text())["skills"]


def test_uninstall_preserves_modified_mcp_entry(tmp_path, monkeypatch):
    install = load_script("install")
    uninstall = load_script("uninstall")
    base = tmp_path / "data"
    base.mkdir()
    source = base / "skill"
    source.mkdir()
    manifest = {"owner": "laya-router-skill", "paths": [str(source)], "skills": {},
                "mcp": {"laya-router": {"agent": "codex", "command": "/python",
                                        "sha256": install.digest(b"original MCP config")}}, "launchers": {}}
    (base / "install-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    calls = []
    def fake_run(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, stdout="modified MCP config with /python")
    monkeypatch.setattr(uninstall, "data_dir", lambda: base)
    monkeypatch.setattr(uninstall.shutil, "which", lambda _: "/codex")
    monkeypatch.setattr(uninstall.subprocess, "run", fake_run)
    assert uninstall.main(["--all"]) == 0
    assert calls == [["codex", "mcp", "get", "laya-router"]]
    assert source.exists()
