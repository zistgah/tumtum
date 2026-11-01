# Quantum Tumtum

DOI: https://doi.org/10.5281/zenodo.23861046

Project website: https://zistgah.org/tumtum/

GPU-powered quantum circuit simulation examples built with Qiskit Aer.

**Copyright (C) 1993-2026 Abhishek Choudhary. All rights reserved.**

Licensed under the GNU General Public License, version 3. See [`COPYING`](COPYING).

## Try in Google Colab

Choose a GPU runtime in Colab for GPU execution. The notebooks install `qiskit-aer-gpu`; GPU availability depends on the runtime assigned to your Colab session.

- [Bell state](https://colab.research.google.com/github/zistgah/tumtum/blob/main/notebooks/aer-gpu-bell.ipynb)
- [GPU capacity benchmark](https://colab.research.google.com/github/zistgah/tumtum/blob/main/notebooks/gpu-capacity-benchmark.ipynb)
- [QAOA Max-Cut, 27 qubits](https://colab.research.google.com/github/zistgah/tumtum/blob/main/notebooks/qaoa-maxcut-27.ipynb)

## Examples

- [`aer-gpu-bell`](examples/aer-gpu-bell/README.md) — a Bell-state circuit and a check that Aer detects the GPU.
- [`gpu-capacity-benchmark`](examples/gpu-capacity-benchmark/README.md) — a VRAM-capped benchmark that finds a safe statevector size.
- [`qaoa-maxcut-27`](examples/qaoa-maxcut-27/README.md) — one-layer QAOA Max-Cut on a 27-node cycle.

The QAOA sample was run on an NVIDIA GeForce RTX 3050 using 8,192 shots. It measured a mean cut of 20.238/27, compared with a random-assignment baseline of 13.5/27, and sampled the cycle's 26/27 optimum 23 times. Benchmark outputs are included next to their examples.

## Requirements

- x86_64 Linux (including WSL2 with GPU compute configured)
- NVIDIA GPU and compatible driver; CUDA support for the Aer GPU wheel
- Python 3 and Qiskit Aer GPU

The GPU wheel is available for Linux, not native Windows. Follow the sample README for install and run details. In this account's WSL environment, Qiskit Aer is installed in a pipx-managed environment; activate it with:

```bash
source /home/ac/.local/share/pipx/venvs/qiskit-aer-gpu/bin/activate
```

Open the repository folder in VS Code connected to WSL. The root `.vscode/launch.json` provides F5 configurations for all three examples.

## License

This project is distributed under GPL-3.0-only. See [`COPYING`](COPYING) for the full license text.