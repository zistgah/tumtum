#!/usr/bin/env python3
"""Safely benchmark Qiskit Aer GPU statevector sizes within a VRAM budget."""

from __future__ import annotations

import argparse
import csv
import gc
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


@dataclass(frozen=True)
class GpuMemory:
    total_mb: int
    free_mb: int


def read_gpu_memory() -> GpuMemory:
    executable = shutil.which("nvidia-smi")
    if executable is None and Path("/usr/lib/wsl/lib/nvidia-smi").is_file():
        executable = "/usr/lib/wsl/lib/nvidia-smi"
    if executable is None:
        raise RuntimeError("nvidia-smi was not found; install/configure the NVIDIA driver.")

    completed = subprocess.run(
        [
            executable,
            "--query-gpu=memory.total,memory.free",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    )
    first_gpu = completed.stdout.strip().splitlines()[0]
    total, free = (int(value.strip()) for value in first_gpu.split(",", maxsplit=1))
    return GpuMemory(total_mb=total, free_mb=free)


def make_circuit(qubits: int) -> QuantumCircuit:
    circuit = QuantumCircuit(qubits)
    circuit.h(0)
    for qubit in range(1, qubits):
        circuit.h(qubit)
        circuit.cx(qubit - 1, qubit)
    circuit.measure_all()
    return circuit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Benchmark the largest Aer GPU statevector that fits a VRAM safety budget."
    )
    parser.add_argument("--min-qubits", type=int, default=8)
    parser.add_argument("--max-qubits", type=int, default=32)
    parser.add_argument(
        "--max-vram-percent",
        type=float,
        default=60.0,
        help="Maximum fraction of total VRAM this benchmark may budget (default: 60%%).",
    )
    parser.add_argument(
        "--reserve-mb",
        type=int,
        default=1024,
        help="Keep at least this much of currently free VRAM unused (default: 1024 MB).",
    )
    parser.add_argument(
        "--precision",
        choices=("single", "double"),
        default="double",
        help="Aer statevector precision (double uses about 16 bytes per amplitude).",
    )
    parser.add_argument(
        "--overhead-factor",
        type=float,
        default=1.5,
        help="Conservative multiplier for simulator/workspace overhead (default: 1.5).",
    )
    parser.add_argument("--csv", type=Path, help="Optional path to save successful trial timings.")
    args = parser.parse_args()

    if args.min_qubits < 1 or args.max_qubits < args.min_qubits:
        parser.error("Require 1 <= --min-qubits <= --max-qubits.")
    if not 0 < args.max_vram_percent <= 100:
        parser.error("--max-vram-percent must be greater than 0 and at most 100.")
    if args.reserve_mb < 0 or args.overhead_factor < 1:
        parser.error("--reserve-mb must be nonnegative and --overhead-factor at least 1.")
    return args


def is_memory_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(
        marker in message
        for marker in ("out of memory", "memory allocation", "cuda_error_out_of_memory", "cuda error: 2")
    )


def main() -> int:
    args = parse_args()
    memory = read_gpu_memory()
    safety_budget_mb = min(
        memory.total_mb * args.max_vram_percent / 100,
        max(0, memory.free_mb - args.reserve_mb),
    )
    bytes_per_amplitude = 8 if args.precision == "single" else 16
    print(f"GPU VRAM: {memory.free_mb} MB free / {memory.total_mb} MB total")
    print(
        f"Safety budget: {safety_budget_mb:.0f} MB "
        f"({args.max_vram_percent:g}% total, reserving {args.reserve_mb} MB free)"
    )
    print(f"Aer statevector precision: {args.precision}; overhead factor: {args.overhead_factor:g}x")
    print("Each trial runs one full-superposition, entangled circuit on GPU.")

    devices = AerSimulator(method="statevector").available_devices()
    if "GPU" not in devices:
        raise RuntimeError(f"Aer does not detect a GPU; available devices: {devices}")
    print(f"Aer devices: {devices}")

    simulator = AerSimulator(method="statevector", device="GPU", precision=args.precision)
    results: list[tuple[int, float, float]] = []
    stop_reason = "Reached --max-qubits."
    for qubits in range(args.min_qubits, args.max_qubits + 1):
        statevector_mb = (2**qubits) * bytes_per_amplitude / (1024**2)
        estimated_mb = statevector_mb * args.overhead_factor
        current_memory = read_gpu_memory()
        current_budget_mb = min(
            current_memory.total_mb * args.max_vram_percent / 100,
            max(0, current_memory.free_mb - args.reserve_mb),
        )
        allowed_mb = min(safety_budget_mb, current_budget_mb)
        if estimated_mb > allowed_mb:
            stop_reason = (
                f"Stopped before {qubits} qubits: estimated {estimated_mb:.0f} MB "
                f"exceeds the current {allowed_mb:.0f} MB safety budget "
                f"({current_memory.free_mb} MB currently free)."
            )
            break

        circuit = make_circuit(qubits)
        started = time.perf_counter()
        try:
            result = simulator.run(circuit, shots=1).result()
            if not result.success:
                raise RuntimeError(f"Aer reported an unsuccessful run: {result.status}")
            elapsed = time.perf_counter() - started
        except Exception as error:
            if not is_memory_error(error):
                raise
            stop_reason = f"GPU allocation failed at {qubits} qubits: {error}"
            print(stop_reason, file=sys.stderr)
            break
        finally:
            del circuit
            gc.collect()

        results.append((qubits, statevector_mb, elapsed))
        print(
            f"{qubits:2} qubits | statevector {statevector_mb:8.1f} MB | "
            f"run {elapsed:7.3f} s"
        )
        del result
        gc.collect()

    print(f"\n{stop_reason}")
    if results:
        print(f"Largest successful trial: {results[-1][0]} qubits")
    else:
        print("No trial completed within the configured safety budget.")

    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as output:
            writer = csv.writer(output)
            writer.writerow(("qubits", "statevector_mb", "elapsed_seconds"))
            writer.writerows((q, f"{size:.3f}", f"{elapsed:.6f}") for q, size, elapsed in results)
        print(f"Trial timings saved to {args.csv}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.SubprocessError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1) from error