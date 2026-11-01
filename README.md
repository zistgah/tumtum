# Quantum Tumtum

Version 0.2.0 DOI: https://doi.org/10.5281/zenodo.23861995

Concept DOI: https://doi.org/10.5281/zenodo.23861045

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

The QAOA sample was run on an NVIDIA GeForce RTX 3050 using 8,192 shots. It measured a mean cut of 20.238/27, compared with a random-assignment baseline of 13.5/27, and sampled the cycle's 26/27 optimum 23 times.

A Colab benchmark run on a GPU reporting 15,360 MiB VRAM completed a 28-qubit double-precision statevector (4,096 MiB). With a 40% VRAM cap, 2,048 MiB reserve, and 1.5x overhead estimate, it stopped before 29 qubits. The GPU model was not reported; per-qubit timings are in [`benchmark-colab-16gb.csv`](examples/gpu-capacity-benchmark/benchmark-colab-16gb.csv). This is one measured configuration, not a guarantee of other GPU capacity.

The [v0.2.0 release archive](https://doi.org/10.5281/zenodo.23861995) has an [OpenTimestamps proof](provenance/Quantum-Tumtum-v0.2.0.tar.gz.ots); Bitcoin confirmation is pending.

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
