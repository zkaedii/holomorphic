#!/usr/bin/env python3
"""
Basic Usage Examples for Holomorphic API Client
Demonstrates fundamental operations
"""

import sys
sys.path.insert(0, '..')

from holomorphic_client import HolomorphicClient
import numpy as np

# Initialize client
client = HolomorphicClient("http://localhost:8000")

# 1. Register and Login
print("="*50)
print("Example 1: Authentication")
print("="*50)

# Register (will fail if user exists, that's ok)
try:
    client.register("alice", "alice@example.com", "AlicePass123!")
    print("✓ User registered")
except Exception as e:
    print(f"⚠ Registration: {e}")

# Login
client.login("alice", "AlicePass123!")
print("✓ Logged in as alice\n")

# 2. Generate and Process Signal
print("="*50)
print("Example 2: Signal Processing")
print("="*50)

# Generate sine wave
signal = client.generate_signal("sine", 1000)
print(f"Generated sine wave: {len(signal)} samples")

# Process with default parameters
result = client.process_signal(signal)
print(f"Processing time: {result['processing_time_ms']:.2f}ms")
print(f"Throughput: {result['samples_per_second']:.0f} samples/sec")
print(f"Output mean: {result['metrics']['mean']:.4f}\n")

# 3. Custom Parameters
print("="*50)
print("Example 3: Custom Parameters")
print("="*50)

# Process with custom parameters
result = client.process_signal(
    signal,
    harmonics=15,
    noise=0.3,
    feedback=0.5
)
print(f"Harmonics: 15")
print(f"Noise: 0.3")
print(f"Feedback: 0.5")
print(f"Processing time: {result['processing_time_ms']:.2f}ms\n")

# 4. View Statistics
print("="*50)
print("Example 4: User Statistics")
print("="*50)

stats = client.get_stats()
print(f"Total processes: {stats['total_processes']}")
print(f"Total samples: {stats['total_samples']:,}")
print(f"Average time: {stats['avg_processing_time']:.2f}ms")
print(f"Min time: {stats['min_processing_time']:.2f}ms")
print(f"Max time: {stats['max_processing_time']:.2f}ms\n")

# 5. View History
print("="*50)
print("Example 5: Processing History")
print("="*50)

history = client.get_history(limit=5)
print(f"Recent processes: {len(history)}")
for i, item in enumerate(history[:3], 1):
    print(f"  {i}. {item['samples_count']} samples in {item['processing_time_ms']:.2f}ms")
print()

# Logout
client.logout()
print("✓ Logged out")
