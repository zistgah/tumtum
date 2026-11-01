from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


def main() -> None:
    probe = AerSimulator(method="statevector")
    devices = probe.available_devices()
    if "GPU" not in devices:
        raise SystemExit(
            "Aer did not detect a GPU. Check the CUDA setup and NVIDIA driver. "
            f"Detected devices: {devices}"
        )

    simulator = AerSimulator(method="statevector", device="GPU")
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.measure_all()

    compiled = transpile(circuit, simulator)
    result = simulator.run(compiled, shots=2048, seed_simulator=42).result()

    print(f"Aer devices: {devices}")
    print(f"Bell-state counts: {result.get_counts(compiled)}")


if __name__ == "__main__":
    main()
