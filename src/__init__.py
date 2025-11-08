"""Audio filter design and processing utilities.

This package provides comprehensive tools for audio filtering:
- FIR filter design (design_fir.py)
- IIR filter design (design_iir.py)
- Plotting and visualization (plots.py)
- Audio generation (generate.py)
"""

# FIR filters
from .design_fir import (
    lowpass as fir_lowpass,
    highpass as fir_highpass,
    bandpass as fir_bandpass,
    bandstop as fir_bandstop,
    notch as fir_notch,
    adaptive_numtaps,
)

# IIR filters - Butterworth
from .design_iir import (
    butter_lowpass,
    butter_highpass,
    butter_bandpass,
    butter_bandstop,
    butter_notch,
)

# IIR filters - Chebyshev Type I
from .design_iir import (
    cheby1_lowpass,
    cheby1_highpass,
    cheby1_bandpass,
    cheby1_bandstop,
)

# IIR filters - Chebyshev Type II
from .design_iir import (
    cheby2_lowpass,
    cheby2_highpass,
    cheby2_bandstop,
)

# IIR filters - Elliptic
from .design_iir import (
    ellip_lowpass,
    ellip_highpass,
    ellip_bandstop,
)

# IIR filters - Bessel
from .design_iir import (
    bessel_lowpass,
    bessel_highpass,
    bessel_bandpass,
)

# Audio EQ filters
from .design_iir import (
    parametric_eq,
    shelving_lowshelf,
    shelving_highshelf,
)

# Plotting utilities
from .plots import (
    plot_freq_phase,
    plot_phase_delay,
    plot_spectrogram,
    plot_waveform,
    plot_before_after_spectrogram,
    plot_frequency_spectrum,
)

__all__ = [
    # FIR
    'fir_lowpass',
    'fir_highpass',
    'fir_bandpass',
    'fir_bandstop',
    'fir_notch',
    'adaptive_numtaps',
    
    # IIR Butterworth
    'butter_lowpass',
    'butter_highpass',
    'butter_bandpass',
    'butter_bandstop',
    'butter_notch',
    
    # IIR Chebyshev I
    'cheby1_lowpass',
    'cheby1_highpass',
    'cheby1_bandpass',
    'cheby1_bandstop',
    
    # IIR Chebyshev II
    'cheby2_lowpass',
    'cheby2_highpass',
    'cheby2_bandstop',
    
    # IIR Elliptic
    'ellip_lowpass',
    'ellip_highpass',
    'ellip_bandstop',
    
    # IIR Bessel
    'bessel_lowpass',
    'bessel_highpass',
    'bessel_bandpass',
    
    # EQ
    'parametric_eq',
    'shelving_lowshelf',
    'shelving_highshelf',
    
    # Plotting
    'plot_freq_phase',
    'plot_phase_delay',
    'plot_spectrogram',
    'plot_waveform',
    'plot_before_after_spectrogram',
    'plot_frequency_spectrum',
]

__version__ = '0.1.0'
