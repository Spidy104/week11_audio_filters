"""FIR filter design utilities using scipy.

Provides common filter designs (lowpass, highpass, bandpass, bandstop, notch)
with sensible defaults for audio processing.
"""
from scipy.signal import firwin, kaiserord
import numpy as np


def lowpass(cutoff: float, fs: float, numtaps: int = 129, beta: float = 8.0) -> np.ndarray:
    """Design a lowpass FIR filter.
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        numtaps: Number of filter taps (filter order + 1)
        beta: Kaiser window beta parameter (higher = sharper transition, more ripple)
    
    Returns:
        FIR filter coefficients
    """
    window = ('kaiser', beta)
    return firwin(numtaps, cutoff, window=window, fs=fs)  # type: ignore


def highpass(cutoff: float, fs: float, numtaps: int = 129, beta: float = 8.0) -> np.ndarray:
    """Design a highpass FIR filter.
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        numtaps: Number of filter taps (filter order + 1)
        beta: Kaiser window beta parameter
    
    Returns:
        FIR filter coefficients
    """
    window = ('kaiser', beta)
    return firwin(numtaps, cutoff, window=window, pass_zero=False, fs=fs)  # type: ignore


def bandpass(f_low: float, f_high: float, fs: float, numtaps: int = 129, beta: float = 8.0) -> np.ndarray:
    """Design a bandpass FIR filter.
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        numtaps: Number of filter taps (filter order + 1)
        beta: Kaiser window beta parameter
    
    Returns:
        FIR filter coefficients
    """
    window = ('kaiser', beta)
    return firwin(numtaps, [f_low, f_high], window=window, pass_zero=False, fs=fs)  # type: ignore


def bandstop(f_low: float, f_high: float, fs: float, numtaps: int = 129, beta: float = 8.0) -> np.ndarray:
    """Design a bandstop (notch) FIR filter.
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        numtaps: Number of filter taps (filter order + 1)
        beta: Kaiser window beta parameter
    
    Returns:
        FIR filter coefficients
    """
    window = ('kaiser', beta)
    return firwin(numtaps, [f_low, f_high], window=window, pass_zero=True, fs=fs)  # type: ignore


def notch(center_freq: float, bandwidth: float, fs: float, numtaps: int = 129, beta: float = 8.0) -> np.ndarray:
    """Design a notch filter (narrow bandstop).
    
    Args:
        center_freq: Center frequency to reject in Hz
        bandwidth: Bandwidth around center frequency in Hz
        fs: Sampling frequency in Hz
        numtaps: Number of filter taps (filter order + 1)
        beta: Kaiser window beta parameter
    
    Returns:
        FIR filter coefficients
    """
    f_low = center_freq - bandwidth / 2
    f_high = center_freq + bandwidth / 2
    return bandstop(f_low, f_high, fs, numtaps, beta)


def adaptive_numtaps(transition_width: float, fs: float, attenuation_db: float = 60.0) -> int:
    """Calculate optimal number of taps based on transition width and attenuation.
    
    Uses Kaiser's formula to estimate required filter order.
    
    Args:
        transition_width: Transition bandwidth in Hz
        fs: Sampling frequency in Hz
        attenuation_db: Desired stopband attenuation in dB
    
    Returns:
        Recommended number of taps (always odd for linear phase)
    """
    numtaps, beta = kaiserord(attenuation_db, transition_width / (0.5 * fs))
    # Ensure odd number of taps for Type I FIR (symmetric, linear phase)
    if numtaps % 2 == 0:
        numtaps += 1
    return numtaps