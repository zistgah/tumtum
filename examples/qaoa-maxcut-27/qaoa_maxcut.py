#!/usr/bin/env python3
"""Run one-layer QAOA for Max-Cut on a 27-node cycle using Aer GPU."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def cycle_edges(qubits: int) -> list[tuple[int, int]]:
    return [(vertex, (vertex + 1) % qubits) for vertex in range(qubits)]


def build_qaoa_circuit(qubits: int, gamma: float, beta: float) -> QuantumCircuit:
    """Prepare |+>^n, apply one cost layer and one X-mixer layer, then measure."""
    circuit = QuantumCircuit(qubits)
    circuit.h(range(qubits))

    # C = sum_(u,v) (1 - Z_u Z_v)/2; the omitted identity contributes only a global phase.
    for left, right in cycle_edges(qubits):
        circuit.rzz(-gamma, left, right)

    for qubit in range(qubits):
        circuit.rx(2 * beta, qubit)
    circuit.measure_all()
    return circuit


def cut_size(bitstring: str, edges: list[tuple[int, int]]) -> int:
    # Qiskit displays classical bits in reverse qubit order.
    bits = bitstring.replace(" ", "")[::-1]
    return sum(bits[left] != bits[right] for left, right in edges)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qubits", type=int, default=27, help="Cycle graph vertices (default: 27).")
    parser.add_argument("--shots", type=int, default=8192, help="Measurement samples (default: 8192).")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--csv", type=Path, help="Optional path to save the sampled cut distribution.")
    args = parser.parse_args()
    if args.qubits < 3:
        parser.error("--qubits must be at least 3.")
    if args.shots < 1:
        parser.error("--shots must be positive.")
    return args


def main() -> int:
    args = parse_args()
    qubits = args.qubits
    edges = cycle_edges(qubits)
    gamma = math.pi / 4
    beta = math.pi / 8

    probe = AerSimulator(method="statevector")
    devices = probe.available_devices()
    if "GPU" not in devices:
        raise RuntimeError(f"Aer does not detect a GPU; available devices: {devices}")

    simulator = AerSimulator(method="statevector", device="GPU")
    circuit = build_qaoa_circuit(qubits, gamma, beta)
    compiled = transpile(circuit, simulator, optimization_level=1)
    result = simulator.run(compiled, shots=args.shots, seed_simulator=args.seed).result()
    if not result.success:
        raise RuntimeError(f"Aer reported an unsuccessful run: {result.status}")
    counts = result.get_counts(compiled)

    distribution: dict[int, int] = defaultdict(int)
    for bitstring, count in counts.items():
        distribution[cut_size(bitstring, edges)] += count

    mean_cut = sum(cut * count for cut, count in distribution.items()) / args.shots
    variance = sum(count * (cut - mean_cut) ** 2 for cut, count in distribution.items()) / args.shots
    standard_error = math.sqrt(variance / args.shots)
    best_cut = max(distribution)
    optimum = qubits if qubits % 2 == 0 else qubits - 1

    print(f"Aer devices: {devices}")
    print(f"Algorithm: QAOA, p=1 | graph: {qubits}-node cycle ({len(edges)} edges)")
    print(f"Parameters: gamma={gamma:.6f}, beta={beta:.6f}")
    print(f"GPU: NVIDIA statevector | shots: {args.shots} | seed: {args.seed}")
    print(f"Random assignment expected cut: {len(edges) / 2:.3f} / {len(edges)}")
    print(f"QAOA mean cut: {mean_cut:.3f} +/- {standard_error:.3f} / {len(edges)}")
    print(f"Mean approximation ratio vs exact cycle optimum ({optimum}): {mean_cut / optimum:.3%}")
    print(f"Best sampled cut: {best_cut} / {len(edges)} ({distribution[best_cut]} samples)")
    print(f"Exact cycle optimum: {optimum} / {len(edges)}")

    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(("cut_size", "samples", "fraction"))
            for cut, count in sorted(distribution.items(), reverse=True):
                writer.writerow((cut, count, f"{count / args.shots:.8f}"))
        print(f"Sample distribution saved to {args.csv}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error