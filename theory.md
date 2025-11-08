# Digital Audio Filtering: Theory and Implementation

## Abstract

This document presents comprehensive theoretical foundations for digital audio signal processing, focusing on finite impulse response (FIR) and infinite impulse response (IIR) filter design, implementation, and analysis. We cover audio signal generation, filter theory, frequency-domain analysis, parametric equalization, and visualization techniques. The treatment emphasizes both mathematical rigor and practical implementation considerations for audio engineering applications.

---

## Table of Contents

1. [Audio Signal Fundamentals](#1-audio-signal-fundamentals)
2. [Synthetic Audio Signal Generation](#2-synthetic-audio-signal-generation)
3. [FIR Filter Theory](#3-fir-filter-theory)
4. [IIR Filter Theory](#4-iir-filter-theory)
5. [Filter Design Methods](#5-filter-design-methods)
6. [Parametric and Shelving Equalization](#6-parametric-and-shelving-equalization)
7. [Filter Application and Chaining](#7-filter-application-and-chaining)
8. [Frequency-Domain Analysis](#8-frequency-domain-analysis)
9. [Visualization and Quality Metrics](#9-visualization-and-quality-metrics)

---

## 1. Audio Signal Fundamentals

### 1.1 Digital Audio Representation

**Discrete-Time Signal**: Audio is represented as a sequence of samples.

$$x[n] = x(nT_s), \quad n \in \mathbb{Z}$$

Where:
- $T_s = 1/f_s$ is the sampling period
- $f_s$ is the sampling frequency (typically 44.1 kHz or 48 kHz)

**Nyquist-Shannon Theorem**: A bandlimited signal with maximum frequency $f_{\max}$ can be perfectly reconstructed if:

$$f_s \geq 2f_{\max}$$

**Audio Bandwidth**: Human hearing range is approximately 20 Hz to 20 kHz, requiring $f_s \geq 40$ kHz.

### 1.2 Frequency Content of Audio

**Speech Signals**:
- **Fundamental frequency (F0)**: 80-250 Hz (male), 150-400 Hz (female)
- **Formants**: Resonant frequencies at 500-4000 Hz
- **Consonants**: High-frequency content at 2-8 kHz
- **Intelligibility band**: 300-3400 Hz (telephone quality)

**Music Signals**:
- **Fundamental notes**: 27.5 Hz (A0) to 4186 Hz (C8) on piano
- **Harmonics**: Integer multiples of fundamental (provide timbre)
- **Percussive transients**: Broadband energy (100 Hz - 10 kHz)
- **Mastering range**: Full spectrum 20 Hz - 20 kHz

**Noise and Interference**:
- **Electrical hum**: 50 Hz (Europe) or 60 Hz (North America) with harmonics
- **White noise**: Uniform power across all frequencies
- **Pink noise**: Power decreases as 1/f (equal energy per octave)
- **Environmental noise**: Low-frequency rumble (< 100 Hz) and broadband

### 1.3 Psychoacoustics

**Critical Bands**: Frequency resolution of human hearing (Bark scale).

$$\text{Bark}(f) = 13 \arctan(0.00076f) + 3.5 \arctan\left(\frac{f}{7500}\right)^2$$

**Masking**: Loud sounds at one frequency mask quieter sounds at nearby frequencies.

**Equal-Loudness Contours** (Fletcher-Munson): Perceived loudness varies with frequency; human hearing is most sensitive at 2-5 kHz.

---

## 2. Synthetic Audio Signal Generation

### 2.1 Speech-Like Signal Synthesis

#### Formant Synthesis

**Formants** are resonant frequencies of the vocal tract. A vowel sound can be approximated by summing sinusoids at formant frequencies.

**Vowel /a/ (as in "father")**:
- F1 = 700 Hz, F2 = 1220 Hz, F3 = 2600 Hz

**Synthesis Equation**:

$$s_{\text{speech}}(t) = \sum_{i=1}^{3} A_i \sin(2\pi F_i t + \phi_i) \cdot e(t)$$

Where:
- $A_i$ are formant amplitudes (decreasing with frequency: $A_i \propto 1/i$)
- $\phi_i$ are random phases
- $e(t)$ is an amplitude envelope (attack-sustain-release)

#### Pitch Modulation

Add fundamental frequency (F0) for voiced sounds:

$$p(t) = \sin(2\pi F_0 t), \quad F_0 \approx 100-250 \text{ Hz}$$

**Combined Signal**:

$$x_{\text{speech}}(t) = p(t) \cdot s_{\text{speech}}(t)$$

#### Fricative Sounds (Consonants)

Use modulated noise for unvoiced sounds (/s/, /f/, /th/):

$$x_{\text{fricative}}(t) = n(t) \cdot \text{BPF}(2000-8000 \text{ Hz})$$

Where $n(t)$ is white Gaussian noise and BPF is a bandpass filter.

### 2.2 Music Signal Synthesis

#### Note Frequencies

**Equal Temperament Tuning**:

$$f_n = f_0 \cdot 2^{n/12}$$

Where:
- $f_0 = 440$ Hz (A4, concert pitch)
- $n$ = semitones from A4 (-48 to +48 for 8 octaves)

**Example Notes**:
- C4 (middle C): $f = 440 \cdot 2^{-9/12} = 261.63$ Hz
- E4: $f = 440 \cdot 2^{-5/12} = 329.63$ Hz
- G4: $f = 440 \cdot 2^{-2/12} = 392.00$ Hz

#### Harmonic Synthesis

**Rich timbre** requires harmonics:

$$x_{\text{note}}(t) = \sum_{k=1}^{N_h} \frac{A_0}{k^{\alpha}} \sin(2\pi k f_0 t)$$

Where:
- $k$ = harmonic number
- $\alpha = 1.0-2.0$ controls spectral roll-off
- $N_h = 10-20$ harmonics

**Typical Values**:
- **Piano**: $\alpha \approx 1.5$, exponential decay envelope
- **Violin**: $\alpha \approx 1.0$, sustained envelope with vibrato
- **Sawtooth wave**: All harmonics with $1/k$ amplitude

#### ADSR Envelope

**Attack-Decay-Sustain-Release** shapes amplitude over time:

$$e(t) = \begin{cases}
\frac{t}{t_A} & 0 \leq t < t_A \text{ (attack)} \\
1 - (1 - S)\frac{t - t_A}{t_D} & t_A \leq t < t_A + t_D \text{ (decay)} \\
S & t_A + t_D \leq t < t_R \text{ (sustain)} \\
S \left(1 - \frac{t - t_R}{t_{rel}}\right) & t_R \leq t < t_R + t_{rel} \text{ (release)} \\
0 & \text{otherwise}
\end{cases}$$

**Typical Values**:
- Piano: $t_A = 10$ ms, $t_D = 100$ ms, $S = 0.7$, $t_{rel} = 500$ ms
- Organ: $t_A = 50$ ms, $S = 1.0$, no decay, $t_{rel} = 200$ ms

### 2.3 Interference: 60 Hz Hum

**Power Line Interference**:

$$x_{\text{hum}}(t) = A_{\text{hum}} \left[\sin(2\pi \cdot 60 \cdot t) + 0.3\sin(2\pi \cdot 120 \cdot t)\right]$$

Where:
- Fundamental at 60 Hz
- Second harmonic at 120 Hz (30% amplitude)
- Typical level: $A_{\text{hum}} = 0.01$ to $0.05$ (relative to signal)

### 2.4 Composite Signal

**Final Test Signal**:

$$x(t) = x_{\text{speech}}(t) + x_{\text{music}}(t) + x_{\text{hum}}(t) + \sigma n(t)$$

Where:
- $\sigma$ controls additive white noise level (SNR)
- Normalize to [-1, +1] to prevent clipping

---

## 3. FIR Filter Theory

### 3.1 Mathematical Representation

**Definition**: A finite impulse response filter has output:

$$y[n] = \sum_{k=0}^{M-1} b_k x[n-k]$$

Where:
- $b_k$ are filter coefficients (taps)
- $M$ is the filter order (number of taps)
- $x[n-k]$ are delayed input samples

**Transfer Function** (Z-domain):

$$H(z) = \sum_{k=0}^{M-1} b_k z^{-k}$$

**Frequency Response**:

$$H(e^{j\omega}) = \sum_{k=0}^{M-1} b_k e^{-j\omega k}$$

Where $\omega = 2\pi f / f_s$ is normalized angular frequency.

### 3.2 FIR Filter Properties

#### Stability

**Always Stable**: FIR filters have no feedback, so bounded input always produces bounded output.

$$|x[n]| < \infty \implies |y[n]| < \infty$$

#### Linear Phase

**Type I FIR** (symmetric coefficients, odd length):

$$b_k = b_{M-1-k}, \quad M \text{ odd}$$

**Phase Response**:

$$\angle H(e^{j\omega}) = -\omega \frac{M-1}{2}$$

**Group Delay** (constant):

$$\tau_g = \frac{M-1}{2} \text{ samples}$$

**Importance**: Linear phase means all frequency components are delayed equally, preserving waveform shape (no phase distortion).

#### Computational Complexity

**Multiplications per output sample**: $M$

**Convolution**: $O(N \cdot M)$ for $N$ input samples

**FFT-based convolution**: $O(N \log N)$ for long signals

### 3.3 FIR Filter Design: Windowing Method

#### Ideal Frequency Response

**Ideal Low-Pass Filter**:

$$H_d(e^{j\omega}) = \begin{cases}
1, & |\omega| \leq \omega_c \\
0, & \omega_c < |\omega| \leq \pi
\end{cases}$$

**Impulse Response** (inverse DTFT):

$$h_d[n] = \frac{\sin(\omega_c n)}{\pi n} = \frac{\omega_c}{\pi} \text{sinc}(\omega_c n)$$

**Problem**: Infinite length and non-causal.

#### Windowing

**Apply window function** to truncate and shift:

$$b[n] = w[n] \cdot h_d[n - (M-1)/2], \quad n = 0, 1, \ldots, M-1$$

#### Window Functions

**Rectangular Window**:

$$w[n] = \begin{cases}
1, & 0 \leq n \leq M-1 \\
0, & \text{otherwise}
\end{cases}$$

**Properties**:
- Narrowest main lobe (best transition width)
- Large side lobes (-13 dB) → poor stopband attenuation
- Gibbs phenomenon (ripples near discontinuities)

**Kaiser Window**:

$$w[n] = \frac{I_0\left(\beta \sqrt{1 - \left(\frac{2n}{M-1} - 1\right)^2}\right)}{I_0(\beta)}$$

Where:
- $I_0$ is the modified Bessel function of the first kind
- $\beta$ controls trade-off between main lobe width and side lobe level

**Kaiser $\beta$ Selection**:

Given desired stopband attenuation $A_s$ (dB):

$$\beta = \begin{cases}
0.1102(A_s - 8.7), & A_s > 50 \\
0.5842(A_s - 21)^{0.4} + 0.07886(A_s - 21), & 21 \leq A_s \leq 50 \\
0, & A_s < 21
\end{cases}$$

**Filter Order Estimation**:

$$M \approx \frac{A_s - 8}{2.285 \Delta \omega} + 1$$

Where $\Delta \omega = 2\pi \Delta f / f_s$ is the normalized transition width.

**Other Common Windows**:

| Window | Stopband Attenuation | Main Lobe Width | Use Case |
|--------|---------------------|-----------------|----------|
| Rectangular | -13 dB | Narrowest | Not recommended |
| Hann | -44 dB | 8π/M | General purpose |
| Hamming | -53 dB | 8π/M | Speech processing |
| Blackman | -74 dB | 12π/M | High attenuation |
| Kaiser (β=5) | -60 dB | Adjustable | Flexible design |

### 3.4 FIR Filter Types

#### Low-Pass Filter

**Passes frequencies below $f_c$**:

$$H_{LP}(f) = \begin{cases}
1, & |f| \leq f_c \\
0, & |f| > f_c
\end{cases}$$

**Application**: Remove high-frequency noise, anti-aliasing.

#### High-Pass Filter

**Spectral inversion of low-pass**:

$$h_{HP}[n] = \delta[n] - h_{LP}[n]$$

Or equivalently: $H_{HP}(e^{j\omega}) = 1 - H_{LP}(e^{j\omega})$

**Application**: Remove DC offset, low-frequency rumble.

#### Band-Pass Filter

**Passes frequencies between $f_1$ and $f_2$**:

$$h_{BP}[n] = h_{LP2}[n] - h_{LP1}[n]$$

Where $h_{LP2}$ has cutoff $f_2$ and $h_{LP1}$ has cutoff $f_1$.

**Application**: Isolate specific frequency range (e.g., vocal band 300-3400 Hz).

#### Band-Stop (Notch) Filter

**Rejects frequencies between $f_1$ and $f_2$**:

$$h_{BS}[n] = \delta[n] - h_{BP}[n]$$

**Application**: Remove 60 Hz hum, eliminate specific interference.

---

## 4. IIR Filter Theory

### 4.1 Mathematical Representation

**Difference Equation**:

$$y[n] = \sum_{k=0}^{M} b_k x[n-k] - \sum_{k=1}^{N} a_k y[n-k]$$

Where:
- $b_k$ are feedforward coefficients (numerator)
- $a_k$ are feedback coefficients (denominator)
- Feedback makes the impulse response infinite duration

**Transfer Function**:

$$H(z) = \frac{\sum_{k=0}^{M} b_k z^{-k}}{1 + \sum_{k=1}^{N} a_k z^{-k}} = \frac{B(z)}{A(z)}$$

**Frequency Response**:

$$H(e^{j\omega}) = \frac{B(e^{j\omega})}{A(e^{j\omega})}$$

### 4.2 IIR Filter Properties

#### Stability

**Condition**: All poles of $H(z)$ must lie inside the unit circle.

$$|z_p| < 1 \text{ for all poles } z_p$$

**Consequence**: Unstable filters produce unbounded output (oscillation or explosion).

#### Phase Response

**Nonlinear Phase**: IIR filters generally have nonlinear phase response, causing phase distortion.

**Group Delay**:

$$\tau_g(\omega) = -\frac{d\phi(\omega)}{d\omega}$$

Where $\phi(\omega) = \angle H(e^{j\omega})$.

**Varies with frequency**, causing different delays for different frequency components.

#### Computational Efficiency

**Lower order than FIR** for equivalent sharpness:
- IIR order $N \approx 4-8$ can match FIR order $M \approx 50-200$

**Fewer multiplications per sample**: $M + N$ vs. $M$ for FIR.

**Trade-off**: Feedback requires careful handling for numerical stability.

### 4.3 Analog Filter Prototypes

IIR filters are typically designed by:
1. Design analog prototype $H_a(s)$
2. Transform to digital domain using bilinear transform or impulse invariance

#### Butterworth Filter

**Maximally flat magnitude** in passband:

$$|H_a(j\omega)|^2 = \frac{1}{1 + \left(\frac{\omega}{\omega_c}\right)^{2N}}$$

**Properties**:
- Monotonic response (no ripple)
- Smooth rolloff: -20N dB/decade
- Moderate phase nonlinearity

**Pole Locations**: Uniformly spaced on unit circle in s-plane at:

$$s_k = \omega_c e^{j\pi(2k + N - 1)/(2N)}, \quad k = 0, 1, \ldots, N-1$$

#### Chebyshev Type I

**Equal-ripple in passband**, monotonic stopband:

$$|H_a(j\omega)|^2 = \frac{1}{1 + \epsilon^2 T_N^2(\omega/\omega_c)}$$

Where $T_N$ is the Chebyshev polynomial of order $N$:

$$T_N(x) = \begin{cases}
\cos(N \cos^{-1} x), & |x| \leq 1 \\
\cosh(N \cosh^{-1} x), & |x| > 1
\end{cases}$$

**Properties**:
- Sharper rolloff than Butterworth
- Passband ripple controlled by $\epsilon$ (typically 0.5-3 dB)
- Steeper: ~20N dB/decade in stopband

**Parameter $\epsilon$**:

$$\epsilon = \sqrt{10^{R_p/10} - 1}$$

Where $R_p$ is passband ripple in dB.

#### Chebyshev Type II

**Monotonic passband**, equal-ripple in stopband:

$$|H_a(j\omega)|^2 = \frac{1}{1 + \frac{1}{\epsilon^2 T_N^2(\omega_s/\omega)}}$$

**Properties**:
- Flat passband (like Butterworth)
- Sharper rolloff than Butterworth
- Stopband ripple controlled by $\epsilon$

#### Elliptic (Cauer)

**Equal-ripple in both passband and stopband**:

$$|H_a(j\omega)|^2 = \frac{1}{1 + \epsilon^2 R_N^2(\omega/\omega_c)}$$

Where $R_N$ is an elliptic rational function.

**Properties**:
- **Sharpest possible rolloff** for given order
- Ripple in both bands
- Most complex to design

#### Bessel Filter

**Maximally flat group delay** (linear phase approximation):

$$\tau_g(\omega) \approx \tau_0 \text{ (constant)}$$

**Transfer Function**: Poles arranged to approximate linear phase.

**Properties**:
- Best time-domain response (minimal overshoot)
- Poor frequency selectivity (gradual rolloff)
- Ideal for pulse/transient signals

### 4.4 Bilinear Transform

**Maps s-plane to z-plane**:

$$z = \frac{1 + sT/2}{1 - sT/2}, \quad s = \frac{2}{T}\frac{z - 1}{z + 1}$$

Where $T = 1/f_s$ is the sampling period.

**Frequency Warping**: Analog frequency $\omega_a$ maps to digital $\omega_d$:

$$\omega_d = 2\tan^{-1}\left(\frac{\omega_a T}{2}\right)$$

**Pre-Warping**: To place cutoff exactly at desired frequency:

$$\omega_a = \frac{2}{T}\tan\left(\frac{\omega_d}{2}\right)$$

**Example**: For $f_c = 1$ kHz at $f_s = 48$ kHz:

$$\omega_c = 2\pi \cdot 1000 / 48000 = 0.1309 \text{ rad/sample}$$

$$\omega_a = \frac{2 \cdot 48000}{1}\tan(0.1309/2) = 6294 \text{ rad/s}$$

### 4.5 Second-Order Sections (SOS)

**Numerical Stability**: High-order IIR filters are sensitive to coefficient quantization. Use cascaded biquads (second-order sections):

$$H(z) = \prod_{i=1}^{L} H_i(z) = \prod_{i=1}^{L} \frac{b_{0,i} + b_{1,i}z^{-1} + b_{2,i}z^{-2}}{1 + a_{1,i}z^{-1} + a_{2,i}z^{-2}}$$

**Benefits**:
- Each biquad is guaranteed stable if designed correctly
- Less susceptible to rounding errors
- Easier to analyze and optimize

**Implementation**: Use `scipy.signal.sosfilt` instead of direct form.

---

## 5. Filter Design Methods

### 5.1 FIR Design with SciPy

**Kaiser Window Method**:

```python
from scipy.signal import firwin, kaiserord

# Estimate order and beta
N, beta = kaiserord(ripple=60, width=transition_width/(0.5*fs))

# Design filter
taps = firwin(N, cutoff, window=('kaiser', beta), fs=fs)
```

**Parks-McClellan (Remez) Algorithm**: Optimal equiripple FIR design.

```python
from scipy.signal import remez

taps = remez(numtaps, bands, desired, fs=fs)
```

### 5.2 IIR Design with SciPy

**Butterworth**:

```python
from scipy.signal import butter

sos = butter(N, cutoff, btype='low', output='sos', fs=fs)
```

**Chebyshev Type I**:

```python
from scipy.signal import cheby1

sos = cheby1(N, rp, cutoff, btype='low', output='sos', fs=fs)
```

**Parameters**:
- `N`: filter order
- `rp`: passband ripple (dB) for Chebyshev
- `cutoff`: cutoff frequency (Hz)
- `btype`: 'low', 'high', 'band', 'stop'

### 5.3 Notch Filter Design

**Specific frequency rejection** (e.g., 60 Hz hum):

```python
from scipy.signal import iirnotch

# Design notch filter
b, a = iirnotch(w0=60, Q=30, fs=fs)

# Or as SOS
sos = iirnotch(w0=60, Q=30, fs=fs, output='sos')
```

**Parameters**:
- `w0`: notch frequency (Hz)
- `Q`: quality factor (controls bandwidth: $BW = w_0/Q$)

**Typical Values**: $Q = 30$ gives $BW = 2$ Hz for 60 Hz notch.

---

## 6. Parametric and Shelving Equalization

### 6.1 Parametric EQ Theory

**Boosts or cuts a specific frequency** with adjustable bandwidth.

**Transfer Function** (digital peaking filter):

$$H(z) = \frac{b_0 + b_1 z^{-1} + b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}}$$

**Design Equations** (Robert Bristow-Johnson's formulas):

$$A = 10^{G/40}$$

$$\omega_0 = 2\pi f_0 / f_s$$

$$\alpha = \frac{\sin\omega_0}{2Q}$$

**Boost ($G > 0$)**:

$$b_0 = 1 + \alpha A, \quad b_1 = -2\cos\omega_0, \quad b_2 = 1 - \alpha A$$

$$a_0 = 1 + \frac{\alpha}{A}, \quad a_1 = -2\cos\omega_0, \quad a_2 = 1 - \frac{\alpha}{A}$$

**Cut ($G < 0$)**: Swap $A$ and $1/A$ in above formulas.

**Parameters**:
- $f_0$: center frequency (Hz)
- $G$: gain (dB), positive for boost, negative for cut
- $Q$: quality factor (controls bandwidth)

**Bandwidth**:

$$BW = \frac{f_0}{Q} \text{ Hz}$$

**High Q** (e.g., Q = 10): Narrow bandwidth, surgical cuts/boosts  
**Low Q** (e.g., Q = 0.7): Wide bandwidth, broad tonal shaping

### 6.2 Shelving EQ Theory

#### Low Shelf

**Boosts/cuts all frequencies below $f_0$**:

$$H_{LS}(z) = A \frac{b_0 + b_1 z^{-1} + b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}}$$

**Design** (for $S = 1$, shelf slope):

$$\omega_0 = 2\pi f_0 / f_s, \quad A = 10^{G/40}$$

$$\alpha = \frac{\sin\omega_0}{2}\sqrt{\frac{A + 1/A}{S}}$$

$$\cos\omega_0 = c, \quad \beta = 2\sqrt{A}\alpha$$

**Boost**:

$$b_0 = A[(A+1) - (A-1)c + \beta]$$

$$b_1 = 2A[(A-1) - (A+1)c]$$

$$b_2 = A[(A+1) - (A-1)c - \beta]$$

$$a_0 = (A+1) + (A-1)c + \beta$$

$$a_1 = -2[(A-1) + (A+1)c]$$

$$a_2 = (A+1) + (A-1)c - \beta$$

#### High Shelf

**Boosts/cuts all frequencies above $f_0$**: Similar formulas with sign changes.

**Applications**:
- **Low shelf**: Bass boost/cut (e.g., +3 dB below 200 Hz)
- **High shelf**: Treble boost/cut (e.g., -2 dB above 8 kHz)

### 6.3 Mastering EQ Chain

**Typical processing chain**:

1. **High-pass filter** (20-40 Hz): Remove sub-sonic rumble
2. **Low shelf** (80-200 Hz): Adjust bass warmth
3. **Parametric EQ** (200-500 Hz): Reduce muddiness (-2 to -4 dB)
4. **Parametric EQ** (2-5 kHz): Enhance presence (+1 to +3 dB)
5. **High shelf** (8-12 kHz): Add air/sparkle (+1 to +2 dB)
6. **Notch filter** (60 Hz): Remove hum if present

---

## 7. Filter Application and Chaining

### 7.1 FIR Filtering: Convolution

**Time-Domain Convolution**:

$$y[n] = (h * x)[n] = \sum_{k=0}^{M-1} h[k] x[n-k]$$

**Implementation**:

```python
import numpy as np

y = np.convolve(x, h, mode='same')
```

**Modes**:
- `'full'`: Length $N + M - 1$ (includes all overlap)
- `'same'`: Length $N$ (same as input)
- `'valid'`: Length $N - M + 1$ (no edge effects)

**Edge Effects**: Convolution assumes zero-padding outside signal bounds. Use windowing or overlap-add for long signals.

### 7.2 IIR Filtering: Direct Form or SOS

**Direct Form II Transposed**:

```python
from scipy.signal import lfilter

y = lfilter(b, a, x)
```

**Second-Order Sections** (recommended):

```python
from scipy.signal import sosfilt

y = sosfilt(sos, x)
```

**Advantages of SOS**:
- Numerically stable for high-order filters
- Less sensitive to coefficient quantization
- Prevents overflow in fixed-point implementations

### 7.3 Zero-Phase Filtering

**Forward-Backward Filtering** (`filtfilt`):

```python
from scipy.signal import sosfiltfilt

y = sosfiltfilt(sos, x)
```

**Process**:
1. Filter signal forward: $y_1 = H(z) \cdot x$
2. Reverse: $y_2 = \text{reverse}(y_1)$
3. Filter reversed signal: $y_3 = H(z) \cdot y_2$
4. Reverse again: $y = \text{reverse}(y_3)$

**Effective Transfer Function**:

$$H_{\text{eff}}(z) = H(z) \cdot H(1/z) = |H(z)|^2$$

**Properties**:
- Zero phase shift: $\angle H_{\text{eff}}(e^{j\omega}) = 0$
- Squared magnitude response (steeper rolloff)
- Not causal (requires entire signal)

### 7.4 Filter Chaining

**Serial Connection**: Apply filters sequentially.

**Effective Transfer Function**:

$$H_{\text{total}}(z) = H_1(z) \cdot H_2(z) \cdot \ldots \cdot H_N(z)$$

**Magnitude Response**:

$$|H_{\text{total}}(e^{j\omega})| = \prod_{i=1}^{N} |H_i(e^{j\omega})|$$

In dB:

$$20\log_{10}|H_{\text{total}}| = \sum_{i=1}^{N} 20\log_{10}|H_i|$$

**Practical Considerations**:
- Order matters for nonlinear phase filters (IIR)
- Cumulative phase distortion can be significant
- Monitor intermediate outputs to avoid overflow
- Consider computational cost vs. single combined filter

**Example Chain**:
1. High-pass (remove DC): 20 Hz cutoff
2. Notch filter: Remove 60 Hz hum
3. Parametric EQ: Boost 3 kHz (+3 dB, Q=2)
4. Low-pass: Anti-imaging filter at 20 kHz

---

## 8. Frequency-Domain Analysis

### 8.1 Discrete Fourier Transform (DFT)

**Definition**:

$X[k] = \sum_{n=0}^{N-1} x[n] e^{-j2\pi kn/N}, \quad k = 0, 1, \ldots, N-1$

**Frequency Resolution**:

$\Delta f = \frac{f_s}{N}$

**Nyquist Frequency**: Maximum representable frequency:

$f_{\text{Nyquist}} = \frac{f_s}{2}$

**Zero-Padding**: Increase frequency resolution without adding information:

$N_{\text{padded}} = 2^{\lceil \log_2 N \rceil} \quad \text{(next power of 2)}$

### 8.2 Fast Fourier Transform (FFT)

**Computational Complexity**:
- DFT: $O(N^2)$ operations
- FFT (Cooley-Tukey): $O(N \log N)$ operations

**Implementation**:

```python
import numpy as np

X = np.fft.fft(x, n=N)  # Forward FFT
freqs = np.fft.fftfreq(N, d=1/fs)  # Frequency axis
magnitude = np.abs(X)
phase = np.angle(X)
```

**Magnitude Spectrum** (dB):

$M_{\text{dB}}[k] = 20\log_{10}|X[k]|$

### 8.3 Spectrograms

**Short-Time Fourier Transform (STFT)**:

$X[m, k] = \sum_{n=0}^{L-1} x[n + mH] w[n] e^{-j2\pi kn/L}$

Where:
- $m$ = frame index
- $H$ = hop size (overlap = $L - H$)
- $w[n]$ = window function (Hann, Hamming)
- $L$ = window length

**Spectrogram** (power spectral density):

$S[m, k] = |X[m, k]|^2$

**Parameters**:
- **Window length**: Trade-off between time and frequency resolution
  - Short window (256-512 samples): Good time resolution, poor frequency resolution
  - Long window (2048-4096 samples): Good frequency resolution, poor time resolution
- **Overlap**: Typically 50-75% (hop size = 25-50% of window length)

**Mel Spectrogram**: Convert frequency axis to perceptually-motivated Mel scale:

$\text{Mel}(f) = 2595 \log_{10}\left(1 + \frac{f}{700}\right)$

### 8.4 Frequency Response Visualization

**Magnitude Response**:

$|H(f)| = \left|\sum_{n=0}^{M-1} h[n] e^{-j2\pi fn/f_s}\right|$

**Phase Response**:

$\phi(f) = \angle H(f) = \arg\left(\sum_{n=0}^{M-1} h[n] e^{-j2\pi fn/f_s}\right)$

**Group Delay**:

$\tau_g(f) = -\frac{1}{2\pi}\frac{d\phi(f)}{df}$

**Implementation**:

```python
from scipy.signal import freqz, sosfreqz

# For FIR (coefficients b)
w, h = freqz(b, worN=8192, fs=fs)

# For IIR (SOS format)
w, h = sosfreqz(sos, worN=8192, fs=fs)

# Plot
import matplotlib.pyplot as plt
plt.semilogx(w, 20*np.log10(abs(h)))
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
```

---

## 9. Visualization and Quality Metrics

### 9.1 Time-Domain Visualization

**Waveform Plot**:

```python
import matplotlib.pyplot as plt

time = np.arange(len(x)) / fs
plt.plot(time, x)
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.title('Waveform')
```

**Envelope Detection**: For visualizing amplitude modulation:

```python
from scipy.signal import hilbert

analytic_signal = hilbert(x)
envelope = np.abs(analytic_signal)
```

### 9.2 Frequency-Domain Visualization

**Magnitude Spectrum**:

```python
X = np.fft.fft(x)
freqs = np.fft.fftfreq(len(x), 1/fs)
magnitude_db = 20*np.log10(np.abs(X))

plt.plot(freqs[:len(freqs)//2], magnitude_db[:len(freqs)//2])
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
```

**Spectrogram**:

```python
from scipy.signal import spectrogram

f, t, Sxx = spectrogram(x, fs, nperseg=1024, noverlap=512)
plt.pcolormesh(t, f, 10*np.log10(Sxx), shading='gouraud')
plt.ylabel('Frequency (Hz)')
plt.xlabel('Time (s)')
plt.colorbar(label='Power (dB)')
```

### 9.3 Filter Comparison Visualization

**Before/After Waveforms**: Overlay original and filtered signals.

**Before/After Spectra**: Show frequency content changes.

**Spectrogram Comparison**: Side-by-side or difference plot.

**Example**:

```python
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Original spectrogram
f, t, Sxx_orig = spectrogram(x_original, fs)
ax1.pcolormesh(t, f, 10*np.log10(Sxx_orig))
ax1.set_title('Original')

# Filtered spectrogram
f, t, Sxx_filt = spectrogram(x_filtered, fs)
ax2.pcolormesh(t, f, 10*np.log10(Sxx_filt))
ax2.set_title('Filtered')
```

### 9.4 Quality Metrics

#### Signal-to-Noise Ratio (SNR)

**Definition**:

$\text{SNR} = 10\log_{10}\left(\frac{\sum_{n}x^2[n]}{\sum_{n}(x[n] - \hat{x}[n])^2}\right) \text{ dB}$

Where $\hat{x}[n]$ is the filtered/processed signal.

**Interpretation**: Higher SNR indicates less distortion/noise added by processing.

#### Total Harmonic Distortion (THD)

**Definition**: Ratio of harmonic power to fundamental power:

$\text{THD} = \frac{\sqrt{P_2^2 + P_3^2 + P_4^2 + \ldots}}{P_1}$

Where $P_k$ is the power of the $k$-th harmonic.

**Measurement**: Apply pure tone, measure harmonics in output.

#### Frequency Response Accuracy

**Deviation from Ideal**:

$\epsilon(f) = |H_{\text{actual}}(f)| - |H_{\text{ideal}}(f)|$

**Passband Ripple**: Maximum deviation in passband.

**Stopband Attenuation**: Minimum attenuation in stopband.

#### Phase Distortion

**Phase Linearity Error**:

$\epsilon_{\phi}(f) = \phi(f) - \phi_{\text{linear}}(f)$

Where $\phi_{\text{linear}}(f) = -2\pi f \tau_0$ for ideal linear phase with delay $\tau_0$.

#### Perceptual Metrics

**PESQ (Perceptual Evaluation of Speech Quality)**: ITU-T standard for speech quality (1-5 scale).

**PEAQ (Perceptual Evaluation of Audio Quality)**: ITU-R BS.1387 for audio quality.

**Cepstral Distance**: Measure of spectral envelope difference:

$d_c = \sqrt{\sum_{k=0}^{N_c}(c_1[k] - c_2[k])^2}$

Where $c[k]$ are cepstral coefficients.

---

## 10. Advanced Topics

### 10.1 Adaptive Filtering

**Least Mean Squares (LMS)**: Adapt filter coefficients to minimize error:

$\mathbf{w}[n+1] = \mathbf{w}[n] + \mu e[n] \mathbf{x}[n]$

Where:
- $\mathbf{w}$ = filter coefficients
- $\mu$ = step size
- $e[n] = d[n] - y[n]$ = error signal

**Applications**:
- Noise cancellation (ANC)
- Echo cancellation
- Channel equalization

### 10.2 Multirate Signal Processing

**Downsampling** (decimation):

$y[n] = x[Mn]$

**Upsampling** (interpolation):

$y[n] = \begin{cases}
x[n/L], & n = 0, \pm L, \pm 2L, \ldots \\
0, & \text{otherwise}
\end{cases}$

**Polyphase Decomposition**: Efficient implementation of multirate filters.

**Applications**:
- Sample rate conversion
- Oversampling ADC/DAC
- Subband coding

### 10.3 Warped Filters

**Bark Scale Warping**: Mimic frequency resolution of human hearing.

**All-Pass Transformation**:

$z^{-1} \rightarrow A(z) = \frac{z^{-1} - \lambda}{1 - \lambda z^{-1}}$

Where $\lambda$ controls warping ($\lambda = 0$ is no warping).

**Applications**:
- Perceptual audio coding
- Hearing aid processing

### 10.4 Non-Linear Processing

**Dynamic Range Compression**: Reduce amplitude range.

**Soft Clipping**: Gentle saturation (tube amplifier emulation).

**Waveshaping**: Nonlinear transfer function for distortion effects.

---

## 11. Practical Implementation Considerations

### 11.1 Fixed-Point vs. Floating-Point

**Fixed-Point**:
- Integer arithmetic (faster on some hardware)
- Limited dynamic range
- Requires careful scaling to avoid overflow
- Quantization noise

**Floating-Point**:
- IEEE 754 standard (32-bit or 64-bit)
- Large dynamic range (~140 dB for 32-bit float)
- Easier to implement
- Slightly higher computational cost

### 11.2 Real-Time Processing

**Latency**: Time from input to output.

$\text{Latency} = \frac{N_{\text{buffer}}}{f_s} + \tau_{\text{processing}}$

**Buffer Size Trade-off**:
- Small buffers: Low latency but higher CPU usage
- Large buffers: Higher latency but more efficient

**Typical Values**:
- Live monitoring: 64-128 samples (~1-3 ms at 48 kHz)
- Music production: 256-512 samples (~5-10 ms)
- Non-critical: 1024-2048 samples (~20-40 ms)

### 11.3 Coefficient Quantization

**Effect**: Finite precision alters filter response.

**Pole Movement**: Quantization can move poles outside unit circle → instability.

**Mitigation**:
- Use SOS (second-order sections)
- Higher precision arithmetic (64-bit)
- Analyze pole-zero plot after quantization

### 11.4 Overflow and Saturation

**Prevention**:
- Scale inputs to prevent internal overflow
- Use saturation arithmetic (clip to max/min)
- Monitor intermediate values in filter stages

---

## 12. Application-Specific Considerations

### 12.1 Speech Processing

**Intelligibility Enhancement**:
- High-pass filter: 80-100 Hz (remove rumble)
- Parametric EQ: Boost 2-4 kHz (presence/clarity)
- De-esser: Reduce 6-8 kHz (sibilance)

**Noise Reduction**:
- Spectral subtraction
- Wiener filtering
- Adaptive noise cancellation

### 12.2 Music Production

**Mixing**:
- Individual track EQ (corrective and creative)
- Dynamic EQ (frequency-dependent compression)
- Multiband processing

**Mastering**:
- Linear-phase EQ for subtle adjustments
- Mid-side processing for stereo enhancement
- Limiting and maximization

### 12.3 Broadcast and Streaming

**Loudness Standards**:
- EBU R128 (Europe): -23 LUFS target
- ATSC A/85 (USA): -24 LKFS target
- Streaming: Spotify (-14 LUFS), YouTube (-13 LUFS)

**Pre-Emphasis/De-Emphasis**: FM radio noise reduction.

### 12.4 Hearing Aids and Assistive Devices

**Frequency Compression**: Shift high frequencies to audible range.

**Dynamic Range Compression**: Fit wide range into reduced hearing range.

**Feedback Cancellation**: Adaptive notch filters.

---

### Software and Libraries

11. **SciPy Signal Processing Documentation**: https://docs.scipy.org/doc/scipy/reference/signal.html
    - `scipy.signal` module reference

12. **NumPy FFT Documentation**: https://numpy.org/doc/stable/reference/routines.fft.html
    - FFT algorithms and usage

13. **Librosa**: https://librosa.org/
    - Python library for music and audio analysis

14. **PyAudio**: https://people.csail.mit.edu/hubert/pyaudio/
    - Real-time audio I/O

### Online Resources

15. **DSPRelated.com**: https://www.dsprelated.com/
    - Articles, blogs, and forums on DSP

16. **Julius O. Smith III's Website**: https://ccrma.stanford.edu/~jos/
    - Extensive online books on audio DSP

17. **The Scientist and Engineer's Guide to Digital Signal Processing** by Steven W. Smith
    - Free online book: http://www.dspguide.com/

---

## Appendix A: Window Function Properties

### A.1 Comparison Table

| Window | Main Lobe Width | Peak Side Lobe (dB) | Stopband Attenuation (dB) | Scalloping Loss (dB) |
|--------|-----------------|---------------------|---------------------------|----------------------|
| Rectangular | 2π/M | -13 | -21 | 3.92 |
| Bartlett | 4π/M | -27 | -25 | 1.82 |
| Hann | 4π/M | -31 | -44 | 1.42 |
| Hamming | 4π/M | -43 | -53 | 1.75 |
| Blackman | 6π/M | -58 | -74 | 1.10 |
| Kaiser (β=5) | ~5π/M | -50 | -60 | Variable |
| Kaiser (β=8) | ~6.5π/M | -70 | -80 | Variable |

### A.2 Kaiser Window Parameter Selection

**Design Procedure**:

1. Specify desired stopband attenuation $A_s$ (dB)
2. Calculate Kaiser parameter $\beta$:

$\beta = \begin{cases}
0.1102(A_s - 8.7), & A_s > 50 \\
0.5842(A_s - 21)^{0.4} + 0.07886(A_s - 21), & 21 \leq A_s \leq 50 \\
0, & A_s < 21
\end{cases}$

3. Estimate filter order $M$:

$M = \frac{A_s - 8}{2.285 \Delta \omega} + 1$

Where $\Delta \omega = 2\pi \Delta f / f_s$ is the normalized transition width.

---

## Appendix B: Biquad Filter Cookbook

### B.1 Low-Pass Filter

$H(z) = \frac{b_0 + b_1 z^{-1} + b_2 z^{-2}}{1 + a_1 z^{-1} + a_2 z^{-2}}$

**Coefficients**:

$\omega_0 = 2\pi f_0 / f_s$

$\alpha = \frac{\sin\omega_0}{2Q}$

$b_0 = \frac{1 - \cos\omega_0}{2}$

$b_1 = 1 - \cos\omega_0$

$b_2 = \frac{1 - \cos\omega_0}{2}$

$a_0 = 1 + \alpha$

$a_1 = -2\cos\omega_0$

$a_2 = 1 - \alpha$

**Normalize**: Divide all coefficients by $a_0$.

### B.2 High-Pass Filter

$b_0 = \frac{1 + \cos\omega_0}{2}$

$b_1 = -(1 + \cos\omega_0)$

$b_2 = \frac{1 + \cos\omega_0}{2}$

$a_0 = 1 + \alpha$

$a_1 = -2\cos\omega_0$

$a_2 = 1 - \alpha$

### B.3 Band-Pass Filter (Constant Skirt Gain)

$b_0 = \alpha$

$b_1 = 0$

$b_2 = -\alpha$

$a_0 = 1 + \alpha$

$a_1 = -2\cos\omega_0$

$a_2 = 1 - \alpha$

---

## Appendix C: Frequency Warping Table

### C.1 Analog to Digital Frequency Mapping

For bilinear transform with sampling frequency $f_s$:

| Analog Freq (Hz) | Digital Freq (normalized ω) | Warping Factor |
|------------------|----------------------------|----------------|
| 100 | 0.0131 | 1.0000 |
| 1000 | 0.1304 | 1.0014 |
| 5000 | 0.6283 | 1.0172 |
| 10000 | 1.2217 | 1.0682 |
| 20000 | 2.3562 | 1.2732 |

**Note**: Warping becomes significant above $f_s/10$.

---
