import streamlit as st
from pathlib import Path

st.set_page_config(page_title="Combined Dashboard", page_icon="📊", layout="wide")


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


def get_result_style(label: str) -> str:
    if label == "Likely Scam":
        return "result-danger"
    elif label == "Suspicious":
        return "result-warn"
    return "result-good"


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


def classify_combined(score: int) -> str:
    if score >= 60:
        return "Likely Scam"
    elif score >= 30:
        return "Suspicious"
    return "Genuine"


def get_recommendation(label: str) -> str:
    if label == "Likely Scam":
        return "Do not respond, do not send money, do not share credentials, and escalate immediately for verification."
    elif label == "Suspicious":
        return "Pause the transaction or response, verify the sender independently, and review the content carefully."
    return "No strong suspicious indicators detected overall, but continue with normal security awareness."


load_css()

with st.sidebar:
    st.markdown("## 📊 Fusion Center")
    st.caption("Unified Scam Intelligence")
    st.markdown("---")
    st.markdown("### Detection Sources")
    st.markdown("- Email Analyzer")
    st.markdown("- Voice Analyzer")
    st.markdown("- Combined Risk Logic")
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
                <div class="hero-subtitle">Unified Threat Intelligence</div>
                <div class="hero-title">Combined Scam Risk Dashboard</div>
                <div class="hero-text">
                    This dashboard brings together the latest email and voice analysis results
                    into one final scam likelihood assessment for better decision support.
                </div>
            </div>
            <div class="hero-side">
                <div class="hero-side-title">Fusion Signals</div>
                <div class="hero-chip-wrap">
                    <span class="hero-chip">Email Score</span>
                    <span class="hero-chip">Voice Score</span>
                    <span class="hero-chip">Combined Risk</span>
                    <span class="hero-chip">Final Recommendation</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

email_result = st.session_state.get("email_result")
voice_result = st.session_state.get("voice_result")

if not email_result and not voice_result:
    st.warning("No email or voice analysis results found yet. Please analyze an email and/or a voice sample first.")
elif email_result and not voice_result:
    combined_score = int(round(email_result["score"] * 0.60))
    final_label = classify_combined(combined_score)
elif voice_result and not email_result:
    combined_score = int(round(voice_result["score"] * 0.60))
    final_label = classify_combined(combined_score)
else:
    combined_score = int(round((email_result["score"] * 0.5) + (voice_result["score"] * 0.5)))
    final_label = classify_combined(combined_score)

if email_result or voice_result:
    style_class = get_result_style(final_label)
    status_class = get_status_class(final_label)

    c1, c2, c3 = st.columns(3)

    with c1:
        email_score_display = email_result["score"] if email_result else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Email Score</div>
                <div class="metric-value-small">{email_score_display}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        voice_score_display = voice_result["score"] if voice_result else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Voice Score</div>
                <div class="metric-value-small">{voice_score_display}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Final Classification</div>
                <div class="metric-value-small {status_class}">{final_label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("## Final Combined Result")

    p1, p2 = st.columns([1, 1])

    with p1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Combined Risk Score</div>
                <div class="metric-value">{combined_score}/100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with p2:
        st.markdown(
            f'<div class="{style_class}">Final Assessment: {final_label}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Combined Risk Visualization")
    render_progress_bar(combined_score, final_label)

    st.markdown("### Security Recommendation")
    st.info(get_recommendation(final_label))

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("### Latest Email Result")
        if email_result:
            st.write(f"**Classification:** {email_result['classification']}")
            st.write(f"**Score:** {email_result['score']}/100")
            st.write(f"**Sender:** {email_result.get('sender_email', 'N/A')}")
            st.write(f"**Subject:** {email_result.get('subject', 'N/A')}")
            if email_result["triggered_indicators"]:
                for item in email_result["triggered_indicators"][:5]:
                    st.markdown(f"- {item}")
        else:
            st.info("No email analysis result saved yet.")

    with right:
        st.markdown("### Latest Voice Result")
        if voice_result:
            st.write(f"**Classification:** {voice_result['classification']}")
            st.write(f"**Score:** {voice_result['score']}/100")
            st.write(f"**Acoustic Score:** {voice_result['acoustic_score']}/100")
            st.write(f"**Content Score:** {voice_result['content_score']}/100")
            if voice_result.get("transcript"):
                st.write(f"**Transcript:** {voice_result['transcript']}")
            if voice_result["triggered_indicators"]:
                for item in voice_result["triggered_indicators"][:5]:
                    st.markdown(f"- {item}")
        else:
            st.info("No voice analysis result saved yet.")

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