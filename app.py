"""Streamlit GUI for audio filtering.

Upload an audio file, apply FIR or IIR filters, and listen to the results.
Visualize frequency responses and spectrograms.

CLI usage (provided via pyproject script `audio-filter-app`):
    audio-filter-app --host global --port 8501

Host resolution rules:
    --host local   -> 127.0.0.1 (default)
    --host global  -> 0.0.0.0 (public)
Environment overrides: STREAMLIT_HOST / STREAMLIT_PORT.
"""

from __future__ import annotations

import os
import sys
import tempfile
import numpy as np
import soundfile as sf
import streamlit as st
from scipy.signal import sosfilt

from src.design_fir import bandstop as fir_bandstop, lowpass as fir_lowpass, highpass as fir_highpass
from src.design_iir import (
    butter_bandstop,
    butter_lowpass,
    butter_highpass,
    butter_notch,
    parametric_eq,
    shelving_lowshelf,
    shelving_highshelf,
)
from src.plots import plot_freq_phase, plot_before_after_spectrogram


def _resolve_host(host_option: str | None) -> str:
    """Map shorthand host options to concrete addresses.

    Accepts common aliases. Falls back to loopback when None/empty.
    """
    if not host_option:
        return "127.0.0.1"
    option = host_option.strip().lower()
    if option in {"global", "public", "all", "0.0.0.0"}:
        return "0.0.0.0"
    if option in {"local", "localhost", "127.0.0.1"}:
        return "127.0.0.1"
    return host_option


def run_app(argv: list[str] | None = None) -> None:
    """Run the Streamlit application with flexible host/port selection.

    Parameters
    ----------
    argv : list[str] | None
        Optional argument vector to override sys.argv[1:]. Supports:
            --host [local|global|IP]
            --port [PORT]
    Environment variables STREAMLIT_HOST / STREAMLIT_PORT also considered.
    """
    from streamlit.web import cli as stcli

    args = list(sys.argv[1:] if argv is None else argv)

    def pop_opt(option: str) -> str | None:
        if option not in args:
            return None
        idx = args.index(option)
        value = None
        if idx + 1 < len(args):
            value = args[idx + 1]
            args.pop(idx + 1)
        args.pop(idx)
        return value

    host_value = pop_opt("--host") or os.getenv("STREAMLIT_HOST")
    host = _resolve_host(host_value)
    port_value = pop_opt("--port") or os.getenv("STREAMLIT_PORT")

    # Preserve any remaining extra args (e.g. --server.headless true) user passed.
    # Mark for the re-executed script that it's running under Streamlit.
    os.environ["STREAMLIT_RUNNING"] = "1"
    sys.argv = ["streamlit", "run", __file__, "--server.address", host]
    if port_value:
        sys.argv.extend(["--server.port", port_value])
    sys.argv.extend(args)
    sys.exit(stcli.main())

def app_main() -> None:
    st.set_page_config(page_title="Audio Filter Lab", layout="wide")
    st.title("Audio Filter Lab - Week 11")

    # Sidebar for filter selection
    st.sidebar.header("Filter Configuration")
    filter_type = st.sidebar.selectbox(
        "Filter Type",
        [
            "FIR Bandstop",
            "FIR Lowpass",
            "FIR Highpass",
            "IIR Bandstop (Butterworth)",
            "IIR Lowpass",
            "IIR Highpass",
            "60Hz Notch Filter",
            "Parametric EQ",
            "Low Shelf",
            "High Shelf",
        ],
    )

    implementation = (
        st.sidebar.radio("Implementation", ["FIR", "IIR"]) if "FIR" in filter_type or "IIR" in filter_type else None
    )

    # File upload
    audio_file = st.file_uploader("Upload Audio File (WAV)", type=["wav"])

    if audio_file:
        # Read audio
        x, fs = sf.read(audio_file)

        # Convert to mono if stereo
        if x.ndim > 1:
            x = x.mean(axis=1)

        # Normalize
        x = x / (np.max(np.abs(x)) + 1e-8)

        # Display original audio
        st.subheader("Original Audio")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.audio(audio_file, format='audio/wav')
        with col2:
            st.metric("Sample Rate", f"{fs} Hz")
            st.metric("Duration", f"{len(x)/fs:.2f} s")
            st.metric("Samples", f"{len(x):,}")

        # Filter parameters
        st.subheader("Filter Parameters")

        # Initialize variables
        h = None
        filter_sos = None
        y = None

        if filter_type == "FIR Bandstop":
            col1, col2, col3 = st.columns(3)
            f1 = col1.slider("Stopband Low (Hz)", 20, int(fs/2) - 100, 900, step=10)
            f2 = col2.slider("Stopband High (Hz)", f1 + 10, int(fs/2), 1100, step=10)
            order = col3.slider("FIR Order", 33, 513, 129, step=16)
            h = fir_bandstop(f1, f2, fs, numtaps=order)
            y = np.convolve(x, h, mode="same")
            filter_sos = None

        elif filter_type == "FIR Lowpass":
            col1, col2 = st.columns(2)
            cutoff = col1.slider("Cutoff Frequency (Hz)", 20, int(fs/2) - 100, 1000, step=10)
            order = col2.slider("FIR Order", 33, 513, 129, step=16)
            h = fir_lowpass(cutoff, fs, numtaps=order)
            y = np.convolve(x, h, mode="same")
            filter_sos = None

        elif filter_type == "FIR Highpass":
            col1, col2 = st.columns(2)
            cutoff = col1.slider("Cutoff Frequency (Hz)", 20, int(fs/2) - 100, 200, step=10)
            order = col2.slider("FIR Order", 33, 513, 129, step=16)
            h = fir_highpass(cutoff, fs, numtaps=order)
            y = np.convolve(x, h, mode="same")
            filter_sos = None

        elif filter_type == "IIR Bandstop (Butterworth)":
            col1, col2, col3 = st.columns(3)
            f1 = col1.slider("Stopband Low (Hz)", 20, int(fs/2) - 100, 900, step=10)
            f2 = col2.slider("Stopband High (Hz)", f1 + 10, int(fs/2), 1100, step=10)
            order = col3.slider("Filter Order", 2, 10, 6)
            sos = butter_bandstop(f1, f2, fs, order=order)
            y = sosfilt(sos, x)
            h = None
            filter_sos = sos

        elif filter_type == "IIR Lowpass":
            col1, col2 = st.columns(2)
            cutoff = col1.slider("Cutoff Frequency (Hz)", 20, int(fs/2) - 100, 1000, step=10)
            order = col2.slider("Filter Order", 2, 10, 6)
            sos = butter_lowpass(cutoff, fs, order=order)
            y = sosfilt(sos, x)
            h = None
            filter_sos = sos

        elif filter_type == "IIR Highpass":
            col1, col2 = st.columns(2)
            cutoff = col1.slider("Cutoff Frequency (Hz)", 20, int(fs/2) - 100, 200, step=10)
            order = col2.slider("Filter Order", 2, 10, 6)
            sos = butter_highpass(cutoff, fs, order=order)
            y = sosfilt(sos, x)
            h = None
            filter_sos = sos

        elif filter_type == "60Hz Notch Filter":
            col1, col2 = st.columns(2)
            center = col1.slider("Center Frequency (Hz)", 50, 70, 60)
            bandwidth = col2.slider("Bandwidth (Hz)", 2, 20, 10)
            sos = butter_notch(center, bandwidth, fs, order=4)
            y = sosfilt(sos, x)
            h = None
            filter_sos = sos

        elif filter_type == "Parametric EQ":
            col1, col2, col3 = st.columns(3)
            center = col1.slider("Center Frequency (Hz)", 100, 10000, 1000, step=10)
            gain_db = col2.slider("Gain (dB)", -12.0, 12.0, 6.0, step=0.5)
            q_factor = col3.slider("Q Factor", 0.5, 10.0, 2.0, step=0.1)
            sos = parametric_eq(center, gain_db, q_factor, fs)
            y = sosfilt(sos, x)
            h = None
            filter_sos = sos

        elif filter_type == "Low Shelf":
            col1, col2 = st.columns(2)
            cutoff = col1.slider("Cutoff Frequency (Hz)", 50, 2000, 200, step=10)
            gain_db = col2.slider("Gain (dB)", -12.0, 12.0, 6.0, step=0.5)
            sos = shelving_lowshelf(cutoff, gain_db, fs)
            y = sosfilt(sos, x)
            h = None
            filter_sos = sos

        elif filter_type == "High Shelf":
            col1, col2 = st.columns(2)
            cutoff = col1.slider("Cutoff Frequency (Hz)", 1000, 10000, 5000, step=10)
            gain_db = col2.slider("Gain (dB)", -12.0, 12.0, -6.0, step=0.5)
            sos = shelving_highshelf(cutoff, gain_db, fs)
            y = sosfilt(sos, x)
            h = None
            filter_sos = sos

        # Ensure y was assigned
        if y is None:
            st.error("Filter processing failed. Please check your parameters.")
            st.stop()

        # Normalize filtered output
        y = y / (np.max(np.abs(y)) + 1e-8)

        # Display filtered audio
        st.subheader("Filtered Audio")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.audio(y.astype(np.float32), format='audio/wav', sample_rate=fs)
        with col2:
            if h is not None:
                st.metric("Group Delay", f"~{len(h)//2 / fs * 1000:.1f} ms")
                st.metric("Filter Taps", len(h))
            elif filter_sos is not None:
                st.metric("Filter Type", "IIR (SOS)")
                st.metric("Sections", len(filter_sos))

        # Download button for filtered audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            sf.write(tmp.name, y, fs)
            with open(tmp.name, 'rb') as f:
                st.download_button(
                    label="Download Filtered Audio",
                    data=f,
                    file_name="filtered_audio.wav",
                    mime="audio/wav",
                )
            os.unlink(tmp.name)

        # Visualizations
        st.subheader("Visualizations")

        viz_tabs = st.tabs(["Spectrograms", "Filter Response"])

        with viz_tabs[0]:
            st.write("### Before vs After Spectrograms")
            with tempfile.TemporaryDirectory() as tmpdir:
                spec_path = os.path.join(tmpdir, "before_after.png")
                plot_before_after_spectrogram(x, y, fs, output_path=spec_path)
                st.image(spec_path, use_container_width=True)

        with viz_tabs[1]:
            if h is not None and filter_sos is not None:
                # Have both FIR and IIR to compare
                st.write("### Filter Frequency Response Comparison")
                with tempfile.TemporaryDirectory() as tmpdir:
                    freq_path = os.path.join(tmpdir, "freq_resp.png")
                    plot_freq_phase(h, filter_sos, fs, output_path=freq_path)
                    st.image(freq_path, use_container_width=True)
            elif h is not None:
                # FIR only
                st.write("### FIR Filter Frequency Response")
                from scipy.signal import freqz
                import matplotlib.pyplot as plt

                w, h_resp = freqz(h, worN=4000, fs=fs)

                fig, ax = plt.subplots(figsize=(12, 5))
                ax.semilogx(w, 20 * np.log10(np.abs(h_resp)), lw=2)
                ax.axhline(-3, color='g', ls=':', label='−3 dB', alpha=0.5)
                ax.axhline(-60, color='r', ls=':', label='−60 dB', alpha=0.5)
                ax.set_title("FIR Filter Frequency Response", fontweight='bold')
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Magnitude (dB)")
                ax.legend()
                ax.grid(True, alpha=0.3, which='both')
                ax.set_xlim(20, fs / 2)
                ax.set_ylim(-100, 5)
                st.pyplot(fig)
                plt.close()
            elif filter_sos is not None:
                # IIR only
                st.write("### IIR Filter Frequency Response")
                from scipy.signal import sosfreqz
                import matplotlib.pyplot as plt

                w, h_resp = sosfreqz(filter_sos, worN=4000, fs=fs)

                fig, ax = plt.subplots(figsize=(12, 5))
                ax.semilogx(w, 20 * np.log10(np.abs(h_resp)), lw=2)
                ax.axhline(-3, color='g', ls=':', label='−3 dB', alpha=0.5)
                ax.axhline(-60, color='r', ls=':', label='−60 dB', alpha=0.5)
                ax.set_title("IIR Filter Frequency Response", fontweight='bold')
                ax.set_xlabel("Frequency (Hz)")
                ax.set_ylabel("Magnitude (dB)")
                ax.legend()
                ax.grid(True, alpha=0.3, which='both')
                ax.set_xlim(20, fs / 2)
                st.pyplot(fig)
                plt.close()
    else:
        st.info("Upload a WAV file to get started")
        st.markdown(
            """
            ### Features:
            - Multiple filter types (FIR & IIR)
            - Real-time spectrogram visualization
            - Listen to before/after audio
            - Download filtered results
            - Filter frequency response plots
            
            ### Supported Filters:
            - **FIR**: Bandstop, Lowpass, Highpass
            - **IIR**: Butterworth filters, Notch, Parametric EQ, Shelving EQ
            """
        )


# Only run the UI when executed by Streamlit (triggered by run_app)
if os.getenv("STREAMLIT_RUNNING") == "1":
    app_main()


"""NOTE: Legacy run_app removed (see top-level run_app)."""