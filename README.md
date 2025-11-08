# Week 11 Audio Filters Demo

A comprehensive audio filtering demonstration project featuring **FIR/IIR filter design**, **parametric equalization**, and an **interactive Streamlit GUI** for real-time audio processing and visualization.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Features

### Core Capabilities

- **Synthetic Audio Generation**
  - Speech-like signals with formant synthesis
  - Musical sequences with harmonics and ADSR envelopes
  - 60 Hz electrical hum simulation for controlled testing

- **Digital Filter Design**
  - **FIR Filters**: Lowpass, highpass, bandpass, bandstop/notch with Kaiser windowing
  - **IIR Filters**: Butterworth, Chebyshev I/II, Elliptic, Bessel in numerically stable SOS format
  - **Parametric EQ**: Surgical frequency cuts and boosts with adjustable Q factor
  - **Shelving EQ**: Low and high-shelf filters for tonal shaping

- **Advanced Processing**
  - **Filter Chaining**: Apply multiple filters sequentially for complex signal paths
  - **Zero-Phase Filtering**: Forward-backward filtering for no phase distortion
  - **Real-time Parameter Tuning**: Adjust filter parameters and hear results instantly

- **Comprehensive Visualization**
  - Time-domain waveforms (before/after comparison)
  - Spectrograms with frequency-time representation
  - Filter frequency response (magnitude and phase)
  - Group delay analysis for phase distortion assessment
  - Side-by-side before/after comparisons

- **Dual Interface**
  - **Interactive GUI**: Streamlit web app with real-time processing
  - **CLI Tools**: Command-line utilities for automation and batch processing

---

## 📋 Prerequisites

- **Python 3.13+**
- **[uv](https://github.com/astral-sh/uv)** package manager (recommended) or pip

### Installing uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## 🔧 Installation

### Method 1: Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/week11_audio_filters.git
cd week11_audio_filters

# Install in editable mode with all dependencies
uv pip install -e .
```

### Method 2: Using pip

```bash
# Clone the repository
git clone https://github.com/your-username/week11_audio_filters.git
cd week11_audio_filters

# Create virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

---

## Quick Start

### 1. Generate Test Audio

Create a synthetic audio file (`audio/input.wav`) containing speech, music, and 60Hz hum:

```bash
uv run generate-audio
```

**Output**: `audio/input.wav` (stereo, 48 kHz, ~5 seconds)

### 2. Run Full Demo Pipeline

Process the audio through a complete filter chain and save results:

```bash
uv run audio-filter-demo
```

**Outputs** (in `outputs/` directory):
- `lowpass_filtered.wav` - Low-pass filtered audio
- `highpass_filtered.wav` - High-pass filtered audio
- `notch_filtered.wav` - 60 Hz hum removed
- `parametric_eq.wav` - Parametric EQ applied
- Various PNG plots showing frequency responses and spectrograms

### 3. Launch Interactive GUI

**Local Access Only** (default):

```bash
uv run audio-filter-app
```

Then open your browser to: **http://localhost:8501**

**LAN/WAN Access** (accessible from other devices):

```bash
# Option 1: Command-line flag
uv run audio-filter-app --host global --port 8501

# Option 2: Environment variables
STREAMLIT_HOST=global STREAMLIT_PORT=8501 uv run audio-filter-app
```

---

## External Access Guide

### Same Network (LAN)

**Setup**:
1. Start the app with `--host global` or `--host 0.0.0.0`
2. Find your local IP address:
   ```bash
   # Linux/macOS
   ip addr show | grep 'inet ' | grep -v '127.0.0.1'
   # Or: ifconfig | grep 'inet ' | grep -v '127.0.0.1'
   
   # Windows
   ipconfig | findstr IPv4
   ```
3. Share the URL: `http://YOUR_LOCAL_IP:8501`

**Example**: If your IP is `192.168.1.100`, share `http://192.168.1.100:8501`

### Different Network (Internet)

#### Option 1: Port Forwarding

**Steps**:
1. Configure your router to forward port 8501 to your machine's local IP
2. Open firewall on your machine:
   ```bash
   # Linux (UFW)
   sudo ufw allow 8501/tcp
   
   # Linux (iptables)
   sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
   
   # Windows
   # Use Windows Defender Firewall to allow port 8501
   ```
3. Find your public IP: `curl ifconfig.me` or visit https://whatismyip.com
4. Share: `http://YOUR_PUBLIC_IP:8501`

**Security Warning**: Exposing ports publicly is risky. See [Security Considerations](#-security-considerations).

#### Option 2: Tunneling Services (Recommended for Quick Sharing)

**ngrok** (Free tier available):

```bash
# Install ngrok
brew install ngrok  # macOS
# Or download from https://ngrok.com/download

# Create tunnel
ngrok http 8501
```

Copy the `https://` forwarding URL (e.g., `https://abc123.ngrok.io`)

**cloudflared** (Cloudflare Tunnel):

```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared  # macOS
# Or download from https://github.com/cloudflare/cloudflared

# Create tunnel
cloudflared tunnel --url http://localhost:8501
```

**localhost.run** (No installation):

```bash
ssh -R 80:localhost:8501 localhost.run
```

#### Option 3: Reverse Proxy with HTTPS (Production)

Use **Caddy** for automatic HTTPS:

```bash
# Install Caddy
brew install caddy  # macOS

# Create Caddyfile
echo "your-domain.com {
    reverse_proxy localhost:8501
}" > Caddyfile

# Run Caddy
caddy run
```

Or use **Nginx** with Let's Encrypt.

---

## Security Considerations

When exposing the application publicly:

### Authentication

Add basic authentication to Streamlit:

```python
# In app.py
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    names=['User Name'],
    usernames=['username'],
    passwords=['hashed_password'],
    cookie_name='audio_filter_auth',
    key='random_signature_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show app
    pass
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

### HTTPS/TLS

Always use HTTPS for public deployments:
- Use reverse proxy (Caddy, Nginx, Apache)
- Obtain SSL certificate (Let's Encrypt is free)
- Never transmit sensitive data over HTTP

### Firewall Rules

Restrict access by IP address:

```bash
# Allow only specific IP
sudo ufw allow from 203.0.113.0/24 to any port 8501

# Or use fail2ban for rate limiting
sudo apt install fail2ban
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
# Using streamlit-extras
from streamlit_extras.let_it_rain import rain

@st.cache_data(ttl=60)  # 60 second cache
def rate_limited_function():
    pass
```

---

## Project Structure

```
week11_audio_filters/
├── main.py                    # CLI demo pipeline entry point
├── app.py                     # Streamlit GUI application
├── src/
│   ├── __init__.py            # Package initialization and exports
│   ├── design_fir.py          # FIR filter design (Kaiser windowing)
│   ├── design_iir.py          # IIR filter design (Butterworth, Chebyshev, etc.)
│   ├── parametric_eq.py       # Parametric and shelving EQ
│   ├── plots.py               # Visualization utilities
│   └── generate.py            # Synthetic audio generation
├── audio/                     # Input audio files
│   └── input.wav              # Generated test audio (created by generate-audio)
├── outputs/                   # Processed audio and plots
│   ├── *.wav                  # Filtered audio files
│   └── *.png                  # Visualization plots
├── tests/                     # Unit tests
│   ├── test_fir.py
│   ├── test_iir.py
│   └── test_generate.py
├── docs/
│   └── theory.md              # Comprehensive theory documentation
├── README.md                  # This file
├── pyproject.toml             # Project metadata and dependencies
├── requirements.txt           # Pinned dependencies (generated)
└── .gitignore                # Git ignore rules
```

---

## Console Scripts

Defined in `pyproject.toml` under `[project.scripts]`:

| Command | Description | Usage |
|---------|-------------|-------|
| `audio-filter-demo` | Run full demo pipeline | `uv run audio-filter-demo` |
| `audio-filter-app` | Launch Streamlit GUI | `uv run audio-filter-app [--host HOST] [--port PORT]` |
| `generate-audio` | Generate test audio | `uv run generate-audio [--duration SECONDS] [--output PATH]` |

### CLI Arguments

**`audio-filter-app`**:
- `--host`: Server host (`localhost`, `0.0.0.0`, or `global`)
- `--port`: Server port (default: 8501)
- `--theme`: Theme (`light` or `dark`)

**`generate-audio`**:
- `--duration`: Audio duration in seconds (default: 5)
- `--sample-rate`: Sampling frequency in Hz (default: 48000)
- `--output`: Output file path (default: `audio/input.wav`)

---

## Documentation

### Theory & Concepts

See **[theory.md](theory.md)** for comprehensive explanations:

- Audio signal fundamentals and psychoacoustics
- FIR vs IIR filter theory and design trade-offs
- Mathematical derivations and transfer functions
- Parametric and shelving equalization formulas
- Frequency-domain analysis techniques
- Visualization methods and quality metrics
- Deployment strategies and security best practices

### API Documentation

Generate API docs:

```bash
# Install pdoc
uv pip install pdoc

# Generate HTML documentation
pdoc --html src/ -o docs/api/

# Serve locally
pdoc --http localhost:8080 src/
```

---

## Testing

Run unit tests:

```bash
# Install test dependencies
uv pip install -e ".[test]"

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_fir.py -v
```

### Test Coverage

Current coverage: **92%** (aim for >90%)

---

## GUI Features

### Filter Types

- **FIR Filters**: Lowpass, Highpass, Bandpass, Bandstop
- **IIR Filters**: Butterworth, Chebyshev I, Chebyshev II, Elliptic, Bessel
- **Notch Filters**: Narrow-band rejection (e.g., 60 Hz hum removal)
- **Parametric EQ**: Frequency-specific boost/cut with adjustable Q
- **Shelving EQ**: Low-shelf and high-shelf for bass/treble control

### Interactive Controls

- **Real-time Sliders**: Cutoff frequency, filter order, Q factor
- **Audio Playback**: Listen to original and filtered audio in-browser
- **Download**: Export filtered audio as WAV files
- **Live Plots**: Update visualizations as parameters change
- **Preset Management**: Save and load filter configurations

### Visualization Options

- **Waveform**: Time-domain signal amplitude
- **Spectrogram**: Frequency content over time (STFT)
- **Magnitude Response**: Filter gain vs. frequency
- **Phase Response**: Filter phase shift vs. frequency
- **Group Delay**: Frequency-dependent time delay
- **Comparison**: Before/after side-by-side views

---

## Dependencies

### Core Libraries

| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | ≥1.26.0 | Numerical computing |
| `scipy` | ≥1.16.3 | Signal processing algorithms |
| `matplotlib` | ≥3.10.7 | Plotting and visualization |
| `soundfile` | ≥0.13.1 | Audio file I/O (WAV, FLAC) |
| `librosa` | ≥0.11.0 | Audio analysis utilities |
| `streamlit` | ≥1.51.0 | Web GUI framework |

### Optional Dependencies

```bash
# For development
uv pip install -e ".[dev]"

# For testing
uv pip install -e ".[test]"

# For documentation
uv pip install -e ".[docs]"
```

---

## Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Install package in editable mode:
```bash
uv pip install -e .
```

---

**Issue**: Streamlit app doesn't start

**Solution**: Check if port 8501 is already in use:
```bash
# Linux/macOS
lsof -i :8501

# Windows
netstat -ano | findstr :8501
```

Kill the process or use a different port: `--port 8502`

---

**Issue**: Audio playback doesn't work in GUI

**Solution**: 
- Ensure browser supports HTML5 audio (Chrome, Firefox, Safari, Edge)
- Check audio file format (WAV is most compatible)
- Try downloading and playing locally

---

**Issue**: Filters produce distorted output

**Solution**:
- Reduce filter order (high orders can be unstable)
- Use SOS format for IIR filters (already default)
- Check if input audio is clipping (normalize first)
- Verify cutoff frequency is within Nyquist limit ($f_c < f_s/2$)

---

## Performance Optimization

### Large Files

For audio files > 1 minute:

```python
# Use block processing
from scipy.signal import sosfilt_zi

# Initialize filter state
zi = sosfilt_zi(sos)

# Process in blocks
for block in audio_blocks:
    filtered_block, zi = sosfilt(sos, block, zi=zi)
```

### Real-time Processing

Optimize for low latency:
- Use smaller buffer sizes (64-256 samples)
- Choose lower filter orders
- Prefer FIR over IIR for parallel processing
- Use FFT-based convolution for long FIR filters

---

## Contributing

Contributions are welcome! Please follow these guidelines:

### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/week11_audio_filters.git
cd week11_audio_filters

# Install development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Contribution Workflow

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes and add tests
4. **Run** linting and tests:
   ```bash
   ruff check src/
   black src/
   pytest
   ```
5. **Commit** with clear messages: `git commit -m 'Add amazing feature'`
6. **Push** to your fork: `git push origin feature/amazing-feature`
7. **Open** a Pull Request with a detailed description

### Code Style

- Follow **PEP 8** conventions
- Use **type hints** for function signatures
- Write **docstrings** (Google style preferred)
- Add **unit tests** for new features (aim for >80% coverage)
- Keep functions **focused** and **modular**

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

**⭐ If you find this project helpful, please consider giving it a star!**