"""Main audio filtering demonstration.

Demonstrates the complete audio filtering pipeline:
1. Load input audio (generated with speech, music, and 60Hz hum)
2. Design multiple FIR and IIR filters
3. Apply filters to audio
4. Save filtered outputs
5. Generate visualizations
"""
import os
import numpy as np
import soundfile as sf
from scipy.signal import sosfilt

# Import our filter design modules
from src import (
    # FIR filters
    fir_lowpass,
    fir_highpass,
    fir_bandstop,
    fir_notch,
    # IIR filters
    butter_lowpass,
    butter_highpass,
    butter_bandstop,
    butter_notch,
    cheby1_lowpass,
    ellip_lowpass,
    bessel_lowpass,
    # EQ filters
    parametric_eq,
    shelving_lowshelf,
    shelving_highshelf,
    # Plotting
    plot_freq_phase,
    plot_phase_delay,
    plot_spectrogram,
    plot_before_after_spectrogram,
    plot_waveform,
    plot_frequency_spectrum,
)


def apply_fir(signal: np.ndarray, taps: np.ndarray) -> np.ndarray:
    """Apply an FIR filter to a signal using convolution."""
    return np.convolve(signal, taps, mode="same")


def apply_iir(signal: np.ndarray, sos: np.ndarray) -> np.ndarray:
    """Apply an IIR filter to a signal using SOS form."""
    return np.asarray(sosfilt(sos, signal))


def main() -> None:
    """Run the complete audio filtering demonstration."""
    print("=" * 60)
    print("AUDIO FILTER DEMO - Week 11")
    print("=" * 60)

    # ==================== Load Audio ====================
    print("\n[1/5] Loading input audio...")
    audio_path = "audio/input.wav"
    if not os.path.exists(audio_path):
        print(f"  WARNING: {audio_path} not found. Generating...")
        os.system("uv run python src/generate.py")

    x, fs = sf.read(audio_path)
    if x.ndim > 1:
        x = x.mean(axis=1)  # Convert to mono
    x = x / (np.max(np.abs(x)) + 1e-8)  # Normalize

    print(f"  OK Loaded: {audio_path}")
    print(f"    Sample rate: {fs} Hz")
    print(f"    Duration: {len(x) / fs:.2f} s")
    print(f"    Samples: {len(x):,}")

    # Create outputs directory
    os.makedirs("outputs", exist_ok=True)

    # ==================== Design Filters ====================
    print("\n[2/5] Designing filters...")

    # FIR filters
    print("  -> FIR filters...")
    h_lp_fir = fir_lowpass(4000, fs, numtaps=129)
    h_hp_fir = fir_highpass(500, fs, numtaps=129)
    h_bs_fir = fir_bandstop(55, 65, fs, numtaps=257)  # Remove 60Hz hum
    h_notch_fir = fir_notch(60, 10, fs, numtaps=257)

    # IIR filters - Butterworth
    print("  -> IIR Butterworth filters...")
    sos_lp_butter = butter_lowpass(4000, fs, order=6)
    sos_hp_butter = butter_highpass(500, fs, order=6)
    sos_bs_butter = butter_bandstop(55, 65, fs, order=4)
    sos_notch_butter = butter_notch(60, 10, fs, order=4)

    # IIR filters - Chebyshev (sharper rolloff)
    print("  -> IIR Chebyshev filters...")
    sos_lp_cheby = cheby1_lowpass(4000, fs, order=5, ripple_db=0.5)

    # IIR filters - Elliptic (sharpest transition)
    print("  -> IIR Elliptic filters...")
    sos_lp_ellip = ellip_lowpass(4000, fs, order=4, ripple_db=0.5, attenuation_db=60)

    # IIR filters - Bessel (best phase response)
    print("  -> IIR Bessel filters...")
    sos_lp_bessel = bessel_lowpass(4000, fs, order=6)

    # EQ filters
    print("  -> EQ filters...")
    sos_peq_boost = parametric_eq(1000, 6, 2.0, fs)  # +6 dB boost at 1 kHz
    sos_peq_cut = parametric_eq(500, -6, 1.5, fs)  # -6 dB cut at 500 Hz
    sos_lowshelf = shelving_lowshelf(200, 6, fs)  # Bass boost
    sos_highshelf = shelving_highshelf(5000, -6, fs)  # Treble cut

    print("  OK Designed 10 FIR/IIR filters and 4 EQ filters")

    # ==================== Apply Filters ====================
    print("\n[3/5] Applying filters to audio...")

    # Apply FIR filters
    print("  -> Applying FIR filters...")
    y_lp_fir = apply_fir(x, h_lp_fir)
    y_hp_fir = apply_fir(x, h_hp_fir)
    y_notch_fir = apply_fir(x, h_notch_fir)
    y_bs_fir = apply_fir(x, h_bs_fir)

    # Apply IIR filters
    print("  -> Applying IIR filters...")
    y_lp_butter = apply_iir(x, sos_lp_butter)
    y_hp_butter = apply_iir(x, sos_hp_butter)
    y_notch_butter = apply_iir(x, sos_notch_butter)
    y_bs_butter = apply_iir(x, sos_bs_butter)

    # Apply different lowpass filter types for comparison
    y_lp_cheby = apply_iir(x, sos_lp_cheby)
    y_lp_ellip = apply_iir(x, sos_lp_ellip)
    y_lp_bessel = apply_iir(x, sos_lp_bessel)

    # Apply EQ filters
    print("  -> Applying EQ filters...")
    y_peq_boost = apply_iir(x, sos_peq_boost)
    y_peq_cut = apply_iir(x, sos_peq_cut)
    y_lowshelf = apply_iir(x, sos_lowshelf)
    y_highshelf = apply_iir(x, sos_highshelf)

    # Create a "mastered" version with multiple EQ stages
    y_mastered = apply_iir(x, sos_notch_butter)  # Remove 60 Hz hum
    y_mastered = apply_iir(y_mastered, sos_lowshelf)  # Bass boost
    y_mastered = apply_iir(y_mastered, parametric_eq(3000, 3, 1.5, fs))  # Presence boost

    print("  OK Processed 14 filtered versions")

    # ==================== Save Outputs ====================
    print("\n[4/5] Saving filtered audio files...")

    outputs = [
        (y_lp_fir, "fir_lowpass_4khz"),
        (y_hp_fir, "fir_highpass_500hz"),
        (y_notch_fir, "fir_notch_60hz"),
        (y_bs_fir, "fir_bandstop_60hz"),
        (y_lp_butter, "iir_butter_lowpass_4khz"),
        (y_hp_butter, "iir_butter_highpass_500hz"),
        (y_notch_butter, "iir_butter_notch_60hz"),
        (y_bs_butter, "iir_butter_bandstop_60hz"),
        (y_lp_cheby, "iir_cheby_lowpass_4khz"),
        (y_lp_ellip, "iir_ellip_lowpass_4khz"),
        (y_lp_bessel, "iir_bessel_lowpass_4khz"),
        (y_peq_boost, "eq_parametric_boost_1khz"),
        (y_peq_cut, "eq_parametric_cut_500hz"),
        (y_lowshelf, "eq_lowshelf_bass_boost"),
        (y_highshelf, "eq_highshelf_treble_cut"),
        (y_mastered, "mastered_full_chain"),
    ]

    for signal, name in outputs:
        signal_norm = signal / (np.max(np.abs(signal)) + 1e-8)
        output_path = f"outputs/{name}.wav"
        sf.write(output_path, signal_norm, fs)

    print(f"  OK Saved {len(outputs)} audio files to outputs/")

    # ==================== Generate Visualizations ====================
    print("\n[5/5] Generating visualizations...")

    # Original audio analysis
    print("  -> Original audio plots...")
    plot_waveform(x, fs, "Original Signal", "outputs/waveform_original.png")
    plot_spectrogram(x, fs, "Original Signal - Spectrogram", "outputs/spectrogram_original.png")
    plot_frequency_spectrum(x, fs, "Original Signal - Frequency Spectrum", "outputs/spectrum_original.png")

    # Filter response comparisons
    print("  -> Filter response plots...")
    plot_freq_phase(h_notch_fir, sos_notch_butter, fs, "outputs/freq_response_notch.png")
    plot_phase_delay(h_notch_fir, sos_notch_butter, fs, "outputs/group_delay_notch.png")

    # Before/after comparisons
    print("  -> Before/after spectrograms...")
    plot_before_after_spectrogram(x, y_notch_butter, fs, "outputs/before_after_notch_60hz.png")
    plot_before_after_spectrogram(x, y_mastered, fs, "outputs/before_after_mastered.png")

    # Filtered audio analysis
    print("  -> Filtered audio plots...")
    plot_spectrogram(y_notch_butter, fs, "60Hz Notch Filtered - Spectrogram", "outputs/spectrogram_notch.png")
    plot_spectrogram(y_mastered, fs, "Mastered - Spectrogram", "outputs/spectrogram_mastered.png")

    print("  OK Generated visualization plots in outputs/")

    # ==================== Summary ====================
    print("\n" + "=" * 60)
    print("COMPLETE! 🎉")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  • {len(outputs)} filtered audio WAV files")
    print("  • 9 visualization plots (PNG)")
    print("\nKey demonstrations:")
    print("  OK FIR filters: Lowpass, Highpass, Bandstop, Notch (60Hz)")
    print("  OK IIR filters: Butterworth, Chebyshev, Elliptic, Bessel")
    print("  OK EQ filters: Parametric EQ, Low Shelf, High Shelf")
    print("  OK Full mastering chain with multiple stages")
    print("\nCheck outputs/ directory for all results!")
    print("Run 'uv run streamlit run app.py' for interactive filtering.")
    print("=" * 60)


if __name__ == "__main__":
    main()