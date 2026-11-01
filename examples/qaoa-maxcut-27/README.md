# QAOA Max-Cut, 27 qubits

A real variational quantum algorithm: one-layer Quantum Approximate Optimization Algorithm (QAOA, p=1) for Max-Cut on a 27-node cycle. It uses Qiskit Aer’s GPU statevector simulator and samples candidate cuts.

This is a simulator experiment, not a physical quantum computer. A 27-qubit statevector has `2^27` complex amplitudes (2 GiB at double precision), which fits the RTX 3050 benchmarked in the companion project.

## Run in WSL

The account's interactive Bash shells activate the existing pipx Qiskit Aer environment:

```bash
cd /shared/qiskit/qaoa-maxcut-27
python qaoa_maxcut.py
```

Or invoke that Python explicitly:

```bash
/home/ac/.local/share/pipx/venvs/qiskit-aer-gpu/bin/python qaoa_maxcut.py --shots 8192 --csv results.csv
```

In VS Code, open this folder in the Ubuntu/WSL window, then press **F5** and choose **QAOA Max-Cut (27 qubits, GPU)**.

## Algorithm

The graph is a 27-vertex cycle, with one edge between each adjacent pair and a closing edge from vertex 26 back to vertex 0. The cost is the number of edges whose endpoints have different measured bits. The circuit prepares a uniform superposition, applies a cost phase-separation layer and an X-mixer layer, then measures. For a cycle, `gamma=pi/4` and `beta=pi/8` are a simple p=1 choice. The program reports mean cut size, sampling error, best observed sample, random-assignment baseline, and exact cycle optimum (26/27 for an odd cycle).

Defaults use 8192 shots and seed 42. The CSV records the sampled cut-size distribution. Try `--shots 32768` for a tighter estimate or `--qubits 26` for an even cycle. More shots increase sampling time but do not increase statevector memory substantially.
## Verified run on the RTX 3050

The 27-qubit GPU run completed with 8192 shots (seed 42): mean cut 20.238/27 (standard error 0.023), compared with the random baseline 13.5/27. The exact odd-cycle optimum is 26/27; the run sampled that optimum 23 times. The per-cut histogram is saved in `results.csv`. These are measurements from one seeded run, not a guarantee of QAOA optimality on other graphs.