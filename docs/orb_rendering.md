# 3D WebGL Orb Rendering Specification

The visual representation of ADITYA OS is powered by a high-performance 3D particle orb.

## Particle System Parameters

- **Base Colors**: Configurable using custom themes or fallback color palettes (e.g. vibrant dark cybernetic blue `#0a192f` mixed with neon blue `#00f0ff`).
- **Speed**: Configurable between `0.1` and `3.0` (adjusts rotation speed and noise vectors).
- **Size**: Default `0.05` particle radius.
- **Particle Count**: Standard mode rendering is capped at `10,000` points. Low-end machines fall back to `2,500` particles.

## WebGL Shader Details

- **Vertex Shader**: Computes 3D positions based on Simplex Noise offsets to simulate organic pulsation.
- **Fragment Shader**: Dynamically colors particles according to their velocity vectors.
