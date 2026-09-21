# Contributing

Issues and pull requests: https://github.com/wangmiaozero/laya-router-skill/issues

Maintainer: wangmiao <tuziling84@gmail.com>

Keep CLI, backend, and adapter layers separate. Preserve fail-open behavior and ownership-safe uninstall. Do not wrap agent commands or make Laya an authorization authority.

For development, use Python 3.11 or 3.12 in a virtual environment. `pip install -e '.[test]'` installs the CLI without a model backend; add `.[mlx]` or `.[torch]` to run real inference. `pytest` never downloads model weights.
