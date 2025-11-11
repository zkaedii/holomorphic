#!/usr/bin/env python3
"""
Signal Visualization Example
Demonstrates how to visualize signals before and after processing
"""

import sys
sys.path.insert(0, '..')

from holomorphic_client import HolomorphicClient
import numpy as np
import matplotlib.pyplot as plt

print("📊 Signal Visualization Example\n")

# Initialize and login
client = HolomorphicClient("http://localhost:8000")
client.login("alice", "AlicePass123!")

# Generate different signal types
signal_types = ["sine", "square", "sawtooth", "chirp"]
fig, axes = plt.subplots(len(signal_types), 2, figsize=(14, 10))
fig.suptitle("Signal Processing Visualization", fontsize=16, fontweight='bold')

for idx, sig_type in enumerate(signal_types):
    # Generate signal
    input_signal = client.generate_signal(sig_type, 1000)

    # Process signal
    result = client.process_signal(
        input_signal,
        harmonics=8,
        noise=0.15,
        feedback=0.3
    )
    output_signal = np.array(result['output'])

    # Plot input
    axes[idx, 0].plot(input_signal, 'b-', linewidth=1)
    axes[idx, 0].set_title(f"{sig_type.capitalize()} - Input Signal", fontweight='bold')
    axes[idx, 0].set_ylabel("Amplitude")
    axes[idx, 0].grid(True, alpha=0.3)
    axes[idx, 0].set_ylim(-1.5, 1.5)

    # Plot output
    axes[idx, 1].plot(output_signal, 'r-', linewidth=1)
    axes[idx, 1].set_title(f"{sig_type.capitalize()} - Processed Signal", fontweight='bold')
    axes[idx, 1].set_ylabel("Amplitude")
    axes[idx, 1].grid(True, alpha=0.3)

    # Add processing info
    info_text = (f"Processing: {result['processing_time_ms']:.2f}ms\n"
                 f"Mean: {result['metrics']['mean']:.3f}\n"
                 f"Std: {result['metrics']['std']:.3f}")
    axes[idx, 1].text(0.02, 0.98, info_text,
                      transform=axes[idx, 1].transAxes,
                      verticalalignment='top',
                      bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
                      fontsize=8)

# Set x-label for bottom plots
axes[-1, 0].set_xlabel("Sample Index")
axes[-1, 1].set_xlabel("Sample Index")

plt.tight_layout()
plt.savefig("signal_processing_visualization.png", dpi=150, bbox_inches='tight')
print("✓ Saved visualization to signal_processing_visualization.png")

# Create comparison plot
fig2, ax = plt.subplots(figsize=(12, 6))

signal = client.generate_signal("sine", 1000)

# Process with different harmonic values
harmonics_values = [1, 5, 10, 15, 20]
colors = plt.cm.viridis(np.linspace(0, 1, len(harmonics_values)))

for h, color in zip(harmonics_values, colors):
    result = client.process_signal(signal, harmonics=h, noise=0.1)
    output = np.array(result['output'])
    ax.plot(output[:200], color=color, linewidth=1.5, label=f"Harmonics={h}", alpha=0.7)

ax.set_title("Effect of Harmonic Parameter (First 200 Samples)", fontsize=14, fontweight='bold')
ax.set_xlabel("Sample Index")
ax.set_ylabel("Amplitude")
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("harmonic_comparison.png", dpi=150, bbox_inches='tight')
print("✓ Saved comparison to harmonic_comparison.png")

plt.show()

client.logout()
print("\n✅ Visualization complete!")
