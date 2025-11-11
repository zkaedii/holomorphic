#!/usr/bin/env python3
"""
Advanced Signal Processing Examples
Demonstrates complex workflows and batch processing
"""

import sys
sys.path.insert(0, '..')

from holomorphic_client import HolomorphicClient, HolomorphicSession
import numpy as np
import matplotlib.pyplot as plt

print("🧠 Advanced Signal Processing Examples\n")

# Using context manager for automatic login/logout
with HolomorphicSession("http://localhost:8000", "alice", "AlicePass123!") as client:

    # Example 1: Compare Different Signal Types
    print("="*60)
    print("Example 1: Processing Different Signal Types")
    print("="*60)

    signal_types = ["sine", "square", "sawtooth", "chirp"]
    results = {}

    for sig_type in signal_types:
        signal = client.generate_signal(sig_type, 1000)
        result = client.process_signal(signal, harmonics=8)
        results[sig_type] = result
        print(f"{sig_type:10s}: {result['processing_time_ms']:6.2f}ms | "
              f"{result['samples_per_second']/1000:8.1f}K samples/sec")

    print()

    # Example 2: Parameter Sweep
    print("="*60)
    print("Example 2: Harmonic Parameter Sweep")
    print("="*60)

    signal = client.generate_signal("sine", 1000)
    harmonic_values = [1, 5, 10, 15, 20]

    for h in harmonic_values:
        result = client.process_signal(signal, harmonics=h)
        print(f"Harmonics={h:2d}: {result['processing_time_ms']:6.2f}ms | "
              f"Mean={result['metrics']['mean']:7.4f}")

    print()

    # Example 3: Batch Processing
    print("="*60)
    print("Example 3: Batch Processing Multiple Signals")
    print("="*60)

    # Generate multiple signals
    signals = [client.generate_signal("sine", 500) for _ in range(10)]

    # Batch process
    batch_results = client.batch_process(signals, harmonics=5, noise=0.1)

    avg_time = sum(r['processing_time_ms'] for r in batch_results) / len(batch_results)
    total_samples = sum(len(s) for s in signals)

    print(f"Processed {len(signals)} signals")
    print(f"Total samples: {total_samples:,}")
    print(f"Average time: {avg_time:.2f}ms")
    print(f"Total time: {sum(r['processing_time_ms'] for r in batch_results):.2f}ms")
    print()

    # Example 4: Create Custom Signal and Process
    print("="*60)
    print("Example 4: Custom Signal Creation")
    print("="*60)

    # Create composite signal
    t = np.linspace(0, 4*np.pi, 2000)
    custom_signal = (
        np.sin(t) +
        0.5 * np.sin(2*t) +
        0.25 * np.sin(4*t) +
        0.1 * np.random.randn(len(t))
    )

    result = client.process_signal(custom_signal, harmonics=12, feedback=0.4)
    print(f"Custom signal: {len(custom_signal)} samples")
    print(f"Processing time: {result['processing_time_ms']:.2f}ms")
    print(f"Output statistics:")
    print(f"  Mean: {result['metrics']['mean']:.4f}")
    print(f"  Std:  {result['metrics']['std']:.4f}")
    print(f"  Min:  {result['metrics']['min']:.4f}")
    print(f"  Max:  {result['metrics']['max']:.4f}")
    print()

    # Example 5: Export Results
    print("="*60)
    print("Example 5: Export Results")
    print("="*60)

    signal = client.generate_signal("chirp", 1000)
    result = client.process_signal(signal, harmonics=10)

    # Export to JSON
    client.export_results(result, "output_result.json", format="json")
    print("✓ Exported to output_result.json")

    # Export to CSV
    client.export_results(result, "output_result.csv", format="csv")
    print("✓ Exported to output_result.csv")
    print()

    # Example 6: Real-time Processing Simulation
    print("="*60)
    print("Example 6: Real-time Processing Simulation")
    print("="*60)

    print("Simulating real-time processing...")
    chunk_size = 500
    num_chunks = 20

    processing_times = []
    for i in range(num_chunks):
        # Generate chunk
        chunk = client.generate_signal("noise", chunk_size)

        # Process chunk
        result = client.process_signal(chunk, harmonics=5)
        processing_times.append(result['processing_time_ms'])

        if (i+1) % 5 == 0:
            avg = sum(processing_times[-5:]) / 5
            print(f"  Chunk {i+1:2d}/{num_chunks}: {avg:.2f}ms avg")

    overall_avg = sum(processing_times) / len(processing_times)
    print(f"\nOverall average: {overall_avg:.2f}ms per chunk")
    print(f"Total samples: {chunk_size * num_chunks:,}")

print("\n✅ All advanced examples completed!")
