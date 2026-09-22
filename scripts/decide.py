#!/usr/bin/env python3
from pathlib import Path
import os
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'runtime'))
from install import data_dir, python_in_venv
from laya_router.cli import main
if __name__ == '__main__':
    private_python = python_in_venv(data_dir() / '.venv')
    if private_python.exists() and Path(sys.executable).resolve() != private_python.resolve():
        os.execv(str(private_python), [str(private_python), '-m', 'laya_router', 'decide', *sys.argv[1:]])
    raise SystemExit(main(['decide', *sys.argv[1:]]))
