import importlib.util
import json
from pathlib import Path
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
