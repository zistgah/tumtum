# Aer GPU capacity benchmark

This project benchmarks the largest Qiskit Aer **statevector simulation** that fits the GPU's memory budget. It does not create or control a physical quantum computer. A qubit simulator stores `2^n` complex amplitudes, so memory use grows exponentially.

## Run

The WSL Bash configuration in this account activates the existing Qiskit Aer environment. In a new WSL terminal:

```bash
cd /shared/qiskit/gpu-capacity-simulator
python benchmark.py
```

In VS Code, open this folder in the Ubuntu/WSL window, then press **F5** and choose **Benchmark Aer GPU capacity**. Its launch profile uses the installed Aer Python directly.

Defaults use double precision, benchmark from 8 through 32 qubits, cap estimated use at 60% of total VRAM, and reserve 1024 MB of currently free VRAM. A conservative 1.5x multiplier accounts for simulator workspace. Before each trial the script reads `nvidia-smi`; it stops before a trial exceeds the budget. It also stops on a GPU memory-allocation error and reports the largest successful trial. Avoid running other GPU-heavy workloads during the benchmark.

Options:

```bash
python benchmark.py --help
python benchmark.py --max-vram-percent 50 --reserve-mb 1536 --precision single
python benchmark.py --max-qubits 30 --csv results.csv
```

The budget is a safeguard, not a guarantee: GPU use by other processes, driver allocations, and simulator overhead vary. Start with the defaults; raise the cap only if you accept the increased out-of-memory risk. If the `nvidia-smi` command is unavailable or Aer does not detect a GPU, the benchmark exits with an explicit error.

## Measured results

On the connected WSL GPU (NVIDIA GeForce RTX 3050, 4096 MB VRAM), the benchmark successfully ran a 27-qubit double-precision statevector (2048 MB) with an 80% VRAM cap and 512 MB reserved. It stopped before 28 qubits because the 1.5x conservative memory estimate exceeded the configured safety budget; 28 qubits was not attempted. The saved per-size timings are in `benchmark-results.csv`. This is the largest run verified under that setting, not proof that no other Aer method or more aggressive memory setting could run larger.

A separate Colab run reported 15,360 MiB total VRAM and completed 28 qubits (4,096 MiB statevector) using double precision, a 40% VRAM cap, a 2,048 MiB reserve, and a 1.5x overhead estimate. It stopped before attempting 29 qubits because the estimated 12,288 MiB exceeded the 6,144 MiB budget. The GPU model was not included in the run output. Timings are recorded in `benchmark-colab-16gb.csv`; this result applies to that run and setting only.
