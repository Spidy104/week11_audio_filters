"""Plotting utilities for audio filter visualization and analysis.

Provides functions for plotting:
- Frequency and phase responses
- Group delay
- Spectrograms and waveforms
- Filter comparisons
"""
import matplotlib.pyplot as plt
import numpy as np
import librosa
import librosa.display
from scipy.signal import freqz, sosfreqz, group_delay
import os


def plot_freq_phase(h_fir, sos_iir, fs: float, output_path: str = "outputs/freq_resp.png"):
    """Plot frequency and phase response comparison of FIR and IIR filters.
    
    Args:
        h_fir: FIR filter coefficients
        sos_iir: IIR filter in SOS format
        fs: Sampling frequency in Hz
        output_path: Path to save the plot
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # FIR frequency response
    w_fir, h_fir_resp = freqz(h_fir, worN=4000, fs=fs)
    
    # IIR frequency response
    w_iir, h_iir_resp = sosfreqz(sos_iir, worN=4000, fs=fs)
    
    # Magnitude plot
    ax1.semilogx(w_fir, 20*np.log10(np.abs(h_fir_resp)), label='FIR (Kaiser)', lw=2)
    ax1.semilogx(w_iir, 20*np.log10(np.abs(h_iir_resp)), '--', label='IIR (Butterworth)', lw=2)
    ax1.axhline(-60, color='r', ls=':', label='−60 dB', alpha=0.5)
    ax1.axhline(-3, color='g', ls=':', label='−3 dB', alpha=0.5)
    ax1.set_title("Frequency Response (Magnitude)", fontsize=14, fontweight='bold')
    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("Magnitude (dB)")
    ax1.legend()
    ax1.grid(True, alpha=0.3, which='both')
    ax1.set_xlim(20, fs/2)
    ax1.set_ylim(-100, 5)
    
    # Phase plot
    ax2.semilogx(w_fir, np.angle(h_fir_resp), label='FIR Phase', lw=2)
    ax2.semilogx(w_iir, np.angle(h_iir_resp), '--', label='IIR Phase', lw=2)
    ax2.set_title("Phase Response", fontsize=14, fontweight='bold')
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Phase (radians)")
    ax2.legend()
    ax2.grid(True, alpha=0.3, which='both')
    ax2.set_xlim(20, fs/2)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved frequency/phase response to {output_path}")


def plot_phase_delay(h_fir, sos_iir, fs: float, output_path: str = "outputs/phase_delay.png"):
    """Plot group delay comparison of FIR and IIR filters.
    
    Args:
        h_fir: FIR filter coefficients
        sos_iir: IIR filter in SOS format
        fs: Sampling frequency in Hz
        output_path: Path to save the plot
    """
    from scipy.signal import sos2tf
    import warnings
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.figure(figsize=(12, 6))
    
    # FIR group delay
    w_fir, gd_fir = group_delay((h_fir, [1]), fs=fs)
    
    # IIR group delay - convert SOS to transfer function first
    # Suppress numerical warnings for very high-order filters
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=UserWarning, message='.*denominator is extremely small.*')
        b, a = sos2tf(sos_iir)
        w_iir, gd_iir = group_delay((b, a), fs=fs)
    
    # Clip extreme values for better visualization
    gd_iir = np.clip(gd_iir, 0, np.percentile(gd_iir[np.isfinite(gd_iir)], 99))
    
    plt.plot(w_fir, gd_fir, label='FIR Group Delay', lw=2)
    plt.plot(w_iir, gd_iir, '--', label='IIR Group Delay', lw=2)
    
    plt.title("Group Delay Comparison", fontsize=14, fontweight='bold')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Group Delay (samples)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, min(8000, fs/2))
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved group delay to {output_path}")


def plot_spectrogram(audio: np.ndarray, fs: float, title: str = "Spectrogram", 
                     output_path: str = "outputs/spectrogram.png"):
    """Plot spectrogram of audio signal.
    
    Args:
        audio: Audio signal
        fs: Sampling frequency in Hz
        title: Plot title
        output_path: Path to save the plot
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.figure(figsize=(14, 6))
    
    # Compute spectrogram
    D = librosa.stft(audio)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    
    # Plot
    img = librosa.display.specshow(S_db, sr=fs, x_axis='time', y_axis='hz', cmap='viridis')
    plt.colorbar(img, format='%+2.0f dB')
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.ylim(0, min(8000, fs/2))
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved spectrogram to {output_path}")


def plot_waveform(audio: np.ndarray, fs: float, title: str = "Waveform",
                  output_path: str = "outputs/waveform.png", max_duration: float = 2.0):
    """Plot time-domain waveform.
    
    Args:
        audio: Audio signal
        fs: Sampling frequency in Hz
        title: Plot title
        output_path: Path to save the plot
        max_duration: Maximum duration to plot in seconds
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Limit to max_duration
    max_samples = int(max_duration * fs)
    audio_plot = audio[:max_samples]
    
    plt.figure(figsize=(14, 4))
    time = np.arange(len(audio_plot)) / fs
    plt.plot(time, audio_plot, lw=0.5, alpha=0.8)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved waveform to {output_path}")


def plot_before_after_spectrogram(before: np.ndarray, after: np.ndarray, fs: float,
                                   output_path: str = "outputs/before_after_spec.png"):
    """Plot before/after spectrograms side by side.
    
    Args:
        before: Original audio signal
        after: Filtered audio signal
        fs: Sampling frequency in Hz
        output_path: Path to save the plot
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Before
    D_before = librosa.stft(before)
    S_db_before = librosa.amplitude_to_db(np.abs(D_before), ref=np.max)
    img1 = librosa.display.specshow(S_db_before, sr=fs, x_axis='time', y_axis='hz', 
                                     cmap='viridis', ax=ax1)
    ax1.set_title("Before Filtering", fontsize=14, fontweight='bold')
    ax1.set_ylim(0, min(8000, fs/2))
    fig.colorbar(img1, ax=ax1, format='%+2.0f dB')
    
    # After
    D_after = librosa.stft(after)
    S_db_after = librosa.amplitude_to_db(np.abs(D_after), ref=np.max)
    img2 = librosa.display.specshow(S_db_after, sr=fs, x_axis='time', y_axis='hz', 
                                     cmap='viridis', ax=ax2)
    ax2.set_title("After Filtering", fontsize=14, fontweight='bold')
    ax2.set_ylim(0, min(8000, fs/2))
    fig.colorbar(img2, ax=ax2, format='%+2.0f dB')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved before/after spectrogram to {output_path}")


def plot_frequency_spectrum(audio: np.ndarray, fs: float, title: str = "Frequency Spectrum",
                            output_path: str = "outputs/spectrum.png"):
    """Plot frequency spectrum (FFT magnitude).
    
    Args:
        audio: Audio signal
        fs: Sampling frequency in Hz
        title: Plot title
        output_path: Path to save the plot
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Compute FFT
    fft = np.fft.rfft(audio)
    magnitude = np.abs(fft)
    freqs = np.fft.rfftfreq(len(audio), 1/fs)
    
    # Convert to dB
    magnitude_db = 20 * np.log10(magnitude + 1e-10)
    
    plt.figure(figsize=(14, 6))
    plt.semilogx(freqs[1:], magnitude_db[1:], lw=1)
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude (dB)")
    plt.grid(True, alpha=0.3, which='both')
    plt.xlim(20, fs/2)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved frequency spectrum to {output_path}")