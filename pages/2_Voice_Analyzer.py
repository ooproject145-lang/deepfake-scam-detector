import os
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.risk_scoring import classify_score, get_result_style
from modules.voice_analyzer import analyze_voice_file

st.set_page_config(page_title="Voice Analyzer", page_icon="🎙️", layout="wide")


def load_css():
    css_file = Path("assets/styles.css")
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def get_status_class(label: str) -> str:
    if label == "Likely Scam":
        return "status-danger"
    elif label == "Suspicious":
        return "status-warn"
    return "status-good"


def get_progress_class(label: str) -> str:
    if label == "Likely Scam":
        return "progress-fill-danger"
    elif label == "Suspicious":
        return "progress-fill-warn"
    return "progress-fill-good"


def render_progress_bar(score: int, label: str):
    progress_class = get_progress_class(label)
    st.markdown(
        f"""
        <div class="progress-shell">
            <div class="{progress_class}" style="width: {score}%;"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


load_css()

with st.sidebar:
    st.markdown("## 🎙️ Voice Shield")
    st.caption("Acoustic + Content Analysis")
    st.markdown("---")

    st.markdown("### Detection Focus")
    st.markdown("- Pitch variation")
    st.markdown("- Energy stability")
    st.markdown("- Spectral texture")
    st.markdown("- Signal regularity")
    st.markdown("- Spoken urgency")
    st.markdown("- Money request keywords")
    st.markdown("---")

    st.markdown("### Project Identity")
    st.info(
        """
**Developer:**  
MUHAMMAD IBN TAOHEED  

**Reg. No:**  
MIU/STD/CMP/CYB/2022/229  

**Department:**  
Department of Cyber Security, Faculty of Computing  

**Institution:**  
Mewar International University, Nigeria  
"""
    )

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-grid">
            <div>
                <div class="hero-subtitle">Acoustic and Semantic Suspicion Analysis</div>
                <div class="hero-title">Voice Scam Detection Console</div>
                <div class="hero-text">
                    Upload a short WAV audio file to analyze both acoustic voice patterns and the spoken message content.
                    This helps detect suspicious money requests, urgency language, and scam-like behavior even when the voice sounds human.
                </div>
            </div>
            <div class="hero-side">
                <div class="hero-side-title">Dual Voice Analysis Mode</div>
                <div class="hero-chip-wrap">
                    <span class="hero-chip">Acoustic Score</span>
                    <span class="hero-chip">Speech-to-Text</span>
                    <span class="hero-chip">Urgency Detection</span>
                    <span class="hero-chip">Financial Cues</span>
                    <span class="hero-chip">Hybrid Risk</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">Voice Sample Input</div>
            <div class="panel-subtitle">
                Upload a short WAV audio clip for lightweight scam analysis.
                The system evaluates both the sound profile and the spoken content.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    audio_file = st.file_uploader("Upload Voice Sample (.wav)", type=["wav"])

    if audio_file:
        st.audio(audio_file, format="audio/wav")

    analyze_btn = st.button("Analyze Voice Sample")

with right:
    st.markdown("### Voice Threat Focus")
    st.caption("Lightweight acoustic and content-based detection")
    st.markdown("---")

    st.info(
        """
**Acoustic Suspicion**  
Detects unusually flat, robotic, or overly consistent voice patterns that may indicate synthetic speech.
"""
    )

    st.info(
        """
**Spoken Scam Language**  
Identifies urgency, secrecy, and financial request phrases from the transcribed audio content.
"""
    )

    st.info(
        """
**Hybrid Risk Estimation**  
Combines voice behavior analysis with spoken content to produce a realistic scam risk score.
"""
    )

if analyze_btn:
    if not audio_file:
        st.warning("Please upload a WAV file before running analysis.")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_path = tmp_file.name

        try:
            result = analyze_voice_file(tmp_path)

            label = classify_score(result.get("score", 0))
            style_class = get_result_style(label)
            status_class = get_status_class(label)

            features = result.get("features") or {}
            transcript = result.get("transcript", "")
            transcription_status = result.get("transcription_status", "Unavailable")
            triggered_indicators = result.get("triggered_indicators") or []
            acoustic_score = result.get("acoustic_score", 0)
            content_score = result.get("content_score", 0)
            final_score = result.get("score", 0)

            st.session_state["voice_result"] = {
                "score": final_score,
                "classification": label,
                "acoustic_score": acoustic_score,
                "content_score": content_score,
                "transcript": transcript,
                "transcription_status": transcription_status,
                "triggered_indicators": triggered_indicators,
                "duration": features.get("Duration (s)", "N/A"),
                "features": features,
            }

            st.markdown("---")
            st.markdown("## Voice Analysis Result")

            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Final Risk Score</div>
                        <div class="metric-value">{final_score}/100</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Classification</div>
                        <div class="metric-value-small {status_class}">{label}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with c3:
                duration_val = features.get("Duration (s)", "N/A")
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Duration</div>
                        <div class="metric-value-small">{duration_val} s</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            s1, s2 = st.columns(2)

            with s1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Acoustic Score</div>
                        <div class="metric-value-small">{acoustic_score}/100</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with s2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">Content Score</div>
                        <div class="metric-value-small">{content_score}/100</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("### Risk Visualization")
            render_progress_bar(final_score, label)

            st.markdown(
                f'<div class="{style_class}">Final Assessment: {label}</div>',
                unsafe_allow_html=True,
            )

            st.markdown("### Speech Transcription")
            if transcript:
                st.markdown(
                    f'<div class="evidence-card"><strong>Transcript:</strong> {transcript}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="evidence-card"><strong>Transcript unavailable:</strong> {transcription_status}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("### Triggered Indicators")
            if triggered_indicators:
                for item in triggered_indicators:
                    st.markdown(
                        f'<div class="evidence-card">{item}</div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    '<div class="result-good">No strong suspicious indicators were detected in this audio sample.</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("### Extracted Acoustic Features")
            if features:
                feature_df = pd.DataFrame(
                    [{"Feature": k, "Value": v} for k, v in features.items()]
                )
                st.dataframe(feature_df, width="stretch", hide_index=True)
            else:
                st.warning("No acoustic features were extracted from this audio.")

        except Exception as e:
            st.error(f"Voice analysis failed: {e}")

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

else:
    st.markdown("---")
    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">Ready for Voice Inspection</div>
            <div class="panel-subtitle">
                Upload a WAV file and run the hybrid lightweight voice scam engine for both acoustic and spoken content analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <hr>
    <div style="text-align: center; font-size: 0.85rem; color: #9ca3af;">
        Deepfake Email and Voice Scam Detection System (Lightweight Version)<br>
        Final Year B.Sc. Project
    </div>
    """,
    unsafe_allow_html=True,
)