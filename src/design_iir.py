"""IIR filter design utilities using scipy.

Provides common IIR filter designs with multiple filter types:
- Butterworth (maximally flat passband)
- Chebyshev Type I (ripple in passband, sharp transition)
- Chebyshev Type II (ripple in stopband, sharp transition)
- Elliptic/Cauer (ripple in both bands, sharpest transition)
- Bessel (maximally flat group delay, linear phase)

All functions return second-order sections (SOS) format for numerical stability.
"""
from scipy.signal import butter, cheby1, cheby2, ellip, bessel
import numpy as np
from typing import Literal


FilterType = Literal['lowpass', 'highpass', 'bandpass', 'bandstop']


# ==================== Butterworth Filters ====================

def butter_lowpass(cutoff: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Butterworth lowpass filter.
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order (higher = sharper transition)
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return butter(order, cutoff / nyq, btype='lowpass', output='sos')  # type: ignore


def butter_highpass(cutoff: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Butterworth highpass filter.
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return butter(order, cutoff / nyq, btype='highpass', output='sos')  # type: ignore


def butter_bandpass(f_low: float, f_high: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Butterworth bandpass filter.
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return butter(order, [f_low / nyq, f_high / nyq], btype='bandpass', output='sos')  # type: ignore


def butter_bandstop(f_low: float, f_high: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Butterworth bandstop (notch) filter.
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return butter(order, [f_low / nyq, f_high / nyq], btype='bandstop', output='sos')  # type: ignore


def butter_notch(center_freq: float, bandwidth: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Butterworth notch filter.
    
    Args:
        center_freq: Center frequency to reject in Hz
        bandwidth: Bandwidth around center frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
    
    Returns:
        Second-order sections representation
    """
    f_low = center_freq - bandwidth / 2
    f_high = center_freq + bandwidth / 2
    return butter_bandstop(f_low, f_high, fs, order)


# ==================== Chebyshev Type I Filters ====================

def cheby1_lowpass(cutoff: float, fs: float, order: int = 6, ripple_db: float = 0.5) -> np.ndarray:
    """Design a Chebyshev Type I lowpass filter (ripple in passband).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        ripple_db: Maximum passband ripple in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return cheby1(order, ripple_db, cutoff / nyq, btype='lowpass', output='sos')  # type: ignore


def cheby1_highpass(cutoff: float, fs: float, order: int = 6, ripple_db: float = 0.5) -> np.ndarray:
    """Design a Chebyshev Type I highpass filter (ripple in passband).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        ripple_db: Maximum passband ripple in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return cheby1(order, ripple_db, cutoff / nyq, btype='highpass', output='sos')  # type: ignore


def cheby1_bandpass(f_low: float, f_high: float, fs: float, order: int = 6, ripple_db: float = 0.5) -> np.ndarray:
    """Design a Chebyshev Type I bandpass filter (ripple in passband).
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        ripple_db: Maximum passband ripple in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return cheby1(order, ripple_db, [f_low / nyq, f_high / nyq], btype='bandpass', output='sos')  # type: ignore


def cheby1_bandstop(f_low: float, f_high: float, fs: float, order: int = 6, ripple_db: float = 0.5) -> np.ndarray:
    """Design a Chebyshev Type I bandstop filter (ripple in passband).
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        ripple_db: Maximum passband ripple in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return cheby1(order, ripple_db, [f_low / nyq, f_high / nyq], btype='bandstop', output='sos')  # type: ignore


# ==================== Chebyshev Type II Filters ====================

def cheby2_lowpass(cutoff: float, fs: float, order: int = 6, attenuation_db: float = 40.0) -> np.ndarray:
    """Design a Chebyshev Type II lowpass filter (ripple in stopband).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        attenuation_db: Minimum stopband attenuation in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return cheby2(order, attenuation_db, cutoff / nyq, btype='lowpass', output='sos')  # type: ignore


def cheby2_highpass(cutoff: float, fs: float, order: int = 6, attenuation_db: float = 40.0) -> np.ndarray:
    """Design a Chebyshev Type II highpass filter (ripple in stopband).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        attenuation_db: Minimum stopband attenuation in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return cheby2(order, attenuation_db, cutoff / nyq, btype='highpass', output='sos')  # type: ignore


def cheby2_bandstop(f_low: float, f_high: float, fs: float, order: int = 6, attenuation_db: float = 40.0) -> np.ndarray:
    """Design a Chebyshev Type II bandstop filter (ripple in stopband).
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        attenuation_db: Minimum stopband attenuation in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return cheby2(order, attenuation_db, [f_low / nyq, f_high / nyq], btype='bandstop', output='sos')  # type: ignore


# ==================== Elliptic (Cauer) Filters ====================

def ellip_lowpass(cutoff: float, fs: float, order: int = 6, ripple_db: float = 0.5, attenuation_db: float = 40.0) -> np.ndarray:
    """Design an elliptic lowpass filter (ripple in both bands, sharpest transition).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        ripple_db: Maximum passband ripple in dB
        attenuation_db: Minimum stopband attenuation in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return ellip(order, ripple_db, attenuation_db, cutoff / nyq, btype='lowpass', output='sos')  # type: ignore


def ellip_highpass(cutoff: float, fs: float, order: int = 6, ripple_db: float = 0.5, attenuation_db: float = 40.0) -> np.ndarray:
    """Design an elliptic highpass filter (ripple in both bands, sharpest transition).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        ripple_db: Maximum passband ripple in dB
        attenuation_db: Minimum stopband attenuation in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return ellip(order, ripple_db, attenuation_db, cutoff / nyq, btype='highpass', output='sos')  # type: ignore


def ellip_bandstop(f_low: float, f_high: float, fs: float, order: int = 6, ripple_db: float = 0.5, attenuation_db: float = 40.0) -> np.ndarray:
    """Design an elliptic bandstop filter (ripple in both bands, sharpest transition).
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
        ripple_db: Maximum passband ripple in dB
        attenuation_db: Minimum stopband attenuation in dB
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return ellip(order, ripple_db, attenuation_db, [f_low / nyq, f_high / nyq], btype='bandstop', output='sos')  # type: ignore


# ==================== Bessel Filters ====================

def bessel_lowpass(cutoff: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Bessel lowpass filter (maximally flat group delay, best phase response).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return bessel(order, cutoff / nyq, btype='lowpass', output='sos', norm='phase')  # type: ignore


def bessel_highpass(cutoff: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Bessel highpass filter (maximally flat group delay, best phase response).
    
    Args:
        cutoff: Cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return bessel(order, cutoff / nyq, btype='highpass', output='sos', norm='phase')  # type: ignore


def bessel_bandpass(f_low: float, f_high: float, fs: float, order: int = 6) -> np.ndarray:
    """Design a Bessel bandpass filter (maximally flat group delay, best phase response).
    
    Args:
        f_low: Lower cutoff frequency in Hz
        f_high: Upper cutoff frequency in Hz
        fs: Sampling frequency in Hz
        order: Filter order
    
    Returns:
        Second-order sections representation
    """
    nyq = fs / 2
    return bessel(order, [f_low / nyq, f_high / nyq], btype='bandpass', output='sos', norm='phase')  # type: ignore


# ==================== Utility Functions ====================

def parametric_eq(center_freq: float, gain_db: float, q_factor: float, fs: float) -> np.ndarray:
    """Design a parametric equalizer (peaking filter).
    
    Boosts or cuts frequencies around a center frequency.
    
    Args:
        center_freq: Center frequency in Hz
        gain_db: Gain in dB (positive = boost, negative = cut)
        q_factor: Quality factor (bandwidth = center_freq / q_factor)
        fs: Sampling frequency in Hz
    
    Returns:
        Second-order sections representation (biquad coefficients)
    """
    import math
    
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * center_freq / fs
    alpha = math.sin(w0) / (2 * q_factor)
    
    b0 = 1 + alpha * A
    b1 = -2 * math.cos(w0)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * math.cos(w0)
    a2 = 1 - alpha / A
    
    # Normalize and convert to SOS format
    sos = np.array([[b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0]])
    return sos


def shelving_lowshelf(cutoff: float, gain_db: float, fs: float, q_factor: float = 0.707) -> np.ndarray:
    """Design a low-shelf filter (boost/cut low frequencies).
    
    Args:
        cutoff: Cutoff frequency in Hz
        gain_db: Gain in dB (positive = boost, negative = cut)
        fs: Sampling frequency in Hz
        q_factor: Quality factor (slope)
    
    Returns:
        Second-order sections representation
    """
    import math
    
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * cutoff / fs
    alpha = math.sin(w0) / 2 * math.sqrt((A + 1/A) * (1/q_factor - 1) + 2)
    
    b0 = A * ((A+1) - (A-1)*math.cos(w0) + 2*math.sqrt(A)*alpha)
    b1 = 2*A * ((A-1) - (A+1)*math.cos(w0))
    b2 = A * ((A+1) - (A-1)*math.cos(w0) - 2*math.sqrt(A)*alpha)
    a0 = (A+1) + (A-1)*math.cos(w0) + 2*math.sqrt(A)*alpha
    a1 = -2 * ((A-1) + (A+1)*math.cos(w0))
    a2 = (A+1) + (A-1)*math.cos(w0) - 2*math.sqrt(A)*alpha
    
    sos = np.array([[b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0]])
    return sos


def shelving_highshelf(cutoff: float, gain_db: float, fs: float, q_factor: float = 0.707) -> np.ndarray:
    """Design a high-shelf filter (boost/cut high frequencies).
    
    Args:
        cutoff: Cutoff frequency in Hz
        gain_db: Gain in dB (positive = boost, negative = cut)
        fs: Sampling frequency in Hz
        q_factor: Quality factor (slope)
    
    Returns:
        Second-order sections representation
    """
    import math
    
    A = 10 ** (gain_db / 40)
    w0 = 2 * math.pi * cutoff / fs
    alpha = math.sin(w0) / 2 * math.sqrt((A + 1/A) * (1/q_factor - 1) + 2)
    
    b0 = A * ((A+1) + (A-1)*math.cos(w0) + 2*math.sqrt(A)*alpha)
    b1 = -2*A * ((A-1) + (A+1)*math.cos(w0))
    b2 = A * ((A+1) + (A-1)*math.cos(w0) - 2*math.sqrt(A)*alpha)
    a0 = (A+1) - (A-1)*math.cos(w0) + 2*math.sqrt(A)*alpha
    a1 = 2 * ((A-1) - (A+1)*math.cos(w0))
    a2 = (A+1) - (A-1)*math.cos(w0) - 2*math.sqrt(A)*alpha
    
    sos = np.array([[b0/a0, b1/a0, b2/a0, 1.0, a1/a0, a2/a0]])
    return sos