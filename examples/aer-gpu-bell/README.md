# Qiskit Aer GPU sample

A minimal Bell-state circuit using Qiskit's Aer statevector simulator on an NVIDIA GPU. The script explicitly checks for GPU availability and fails rather than silently switching to CPU.

## Run and debug in VS Code

1. Open this folder in the WSL window: `/shared/qiskit/qiskit-aer-gpu-sample`.
2. The F5 debug profile explicitly uses `/home/ac/.local/share/pipx/venvs/qiskit-aer-gpu/bin/python`, where the existing pipx-installed Qiskit Aer package is installed. If you use **Run Python File** or the terminal, select that interpreter with `Python: Select Interpreter`.
3. Open `gpu_bell.py`, set a breakpoint, and press **F5**. Choose **Python: Aer GPU Bell sample** if prompted.

For terminal runs, either select the interpreter above and run `python gpu_bell.py`, or invoke it directly:

```bash
/home/ac/.local/share/pipx/venvs/qiskit-aer-gpu/bin/python gpu_bell.py
```

The default system Python (`/usr/bin/python3`) does not have Qiskit installed. The `qiskit-aer-gpu` wheel targets x86_64 Linux with CUDA 12 and a compatible NVIDIA driver. For CUDA 11, install `qiskit-aer-gpu-cu11` instead. GPU wheels are not available for native Windows.