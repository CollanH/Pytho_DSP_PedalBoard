# Pytho DSP PedalBoard

A Python-based real-time DSP pedalboard concept with GUI controls for gain, distortion, and filtering.

## Environment setup

1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Upgrade pip**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Audio backend prerequisites (PortAudio)

`sounddevice` depends on **PortAudio** at runtime.

- **Ubuntu / Debian**
  ```bash
  sudo apt-get update
  sudo apt-get install -y portaudio19-dev
  ```

- **Fedora**
  ```bash
  sudo dnf install -y portaudio-devel
  ```

- **macOS (Homebrew)**
  ```bash
  brew install portaudio
  ```

- **Windows**
  - Most users can install `sounddevice` from wheels directly.
  - If audio device initialization fails, verify your sound drivers and install the latest Microsoft C++ Redistributable.

## Run command

From the project root (with virtualenv active):

```bash
python main.py
```

> If your entry script has a different name, replace `main.py` accordingly.

## Latency tuning tips (buffer size / block size)

Lower values reduce latency but increase CPU load and underrun risk.

- Start with a **block size of 256** samples.
- If you hear crackles/dropouts, try **512** or **1024**.
- For low-latency monitoring on fast systems, try **128**.
- Keep sample rate and block size stable while testing.
- Close CPU-heavy background apps before benchmarking audio performance.

Practical tuning workflow:

1. Begin at 256 samples.
2. Play sustained input and percussive transients.
3. Lower toward 128 until artifacts appear.
4. Step back to the last stable value.

## Expected control behavior

### Gain
- Increases input level before downstream effects.
- Higher gain drives subsequent distortion/filter stages harder.
- Excessive gain may clip if no headroom management is applied.

### Distortion
- Adds non-linear saturation/clipping.
- Low settings produce mild warmth.
- High settings produce stronger harmonics and compression-like feel.
- Can increase perceived loudness and noise floor.

### Filter
- Shapes frequency content (for example low-pass or high-pass behavior depending on implementation).
- Typical expectations:
  - Lower low-pass cutoff = darker tone.
  - Higher high-pass cutoff = thinner tone.
- Resonance/Q (if present) emphasizes frequencies near cutoff.

## Troubleshooting quick checks

- No sound: confirm input/output device selection and OS permissions.
- Crackling: increase block size and ensure CPU is not saturated.
- Startup errors on audio backend: verify PortAudio installation and reinstall `sounddevice`.
