# Backends

| System | Auto backend | Device |
| --- | --- | --- |
| macOS Apple Silicon | laya-mlx | MLX GPU |
| macOS Intel | laya | PyTorch CPU or MPS when available |
| Windows | laya | PyTorch CPU or CUDA when available |
| Linux | laya | PyTorch CPU or CUDA when available |

`backend=mlx` is rejected outside Apple Silicon. `backend=torch` is available on supported systems. `model=auto` delegates to the official Laya Router; `language=en` and `language=multilingual` pass a language hint. The default lazy load downloads only the selected checkpoint when first used. Checkpoint download requires access to Hugging Face unless weights are cached.

The basic checkpoint may be inaccurate on some zero-shot typed-decision tasks. Scores and confidence are advisory signals, not security verdicts.

Sources: [upstream Laya API](https://github.com/NandhaKishorM/laya/blob/main/README.md), [Laya-MLX API](https://github.com/mizorewww/laya-mlx/blob/main/README.md).
