import streamlit as st
from pathlib import Path
from modules.email_analyzer import analyze_email
from modules.risk_scoring import classify_score, get_result_style

st.set_page_config(page_title="Email Analyzer", page_icon="📧", layout="wide")


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
    st.markdown("## 📧 Email Shield")
    st.caption("Text Scam Detection")
    st.markdown("---")

    st.markdown("### Detection Focus")
    st.markdown("- Urgency patterns")
    st.markdown("- Financial requests")
    st.markdown("- Impersonation attempts")
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
                <div class="hero-subtitle">Cybersecurity Threat Intelligence</div>
                <div class="hero-title">Email Scam Analysis Console</div>
                <div class="hero-text">
                    Analyze suspicious emails for urgency pressure, impersonation language,
                    secrecy cues, financial bait, credential lures, and sender-domain mismatch
                    using a lightweight explainable detection engine.
                </div>
            </div>
            <div class="hero-side">
                <div class="hero-side-title">Active Detection Signals</div>
                <div class="hero-chip-wrap">
                    <span class="hero-chip">Urgency</span>
                    <span class="hero-chip">Secrecy</span>
                    <span class="hero-chip">Authority Tone</span>
                    <span class="hero-chip">Financial Request</span>
                    <span class="hero-chip">Credential Trap</span>
                    <span class="hero-chip">Domain Mismatch</span>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.2, 0.8], gap="large")

with left:
    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">Message Input</div>
            <div class="panel-subtitle">
                Provide the sender details and paste the email body for scam risk inspection.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sender_email = st.text_input("Sender Email Address", placeholder="ceo@company.com")
    expected_domain = st.text_input("Expected Trusted Domain", placeholder="company.com")
    subject = st.text_input("Email Subject", placeholder="Urgent confidential payment request")
    body = st.text_area("Email Body", height=280, placeholder="Paste the email content here...")

    analyze_btn = st.button("Analyze Email")

with right:
    st.markdown("### Threat Focus")
    st.caption("Lightweight and explainable detection engine")
    st.markdown("---")

    st.info(
        """
**Impersonation Risk**  
Detects language that imitates authority or pressures the recipient using executive-style commands.
"""
    )

    st.info(
        """
**Sender Validation**  
Compares sender domain with expected domain to detect suspicious mismatches.
"""
    )

    st.info(
        """
**Social Engineering Cues**  
Flags urgency, secrecy, payment instructions, and credential requests commonly used in scams.
"""
    )

if analyze_btn:
    result = analyze_email(sender_email, subject, body, expected_domain)
    label = classify_score(result["score"])
    style_class = get_result_style(label)
    status_class = get_status_class(label)

    st.session_state["email_result"] = {
        "score": result["score"],
        "classification": label,
        "sender_domain": result["sender_domain"] if result["sender_domain"] else "N/A",
        "triggered_indicators": result["triggered_indicators"],
        "subject": subject,
        "sender_email": sender_email,
    }

    st.markdown("---")
    st.markdown("## Analysis Result")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Risk Score</div>
                <div class="metric-value">{result["score"]}/100</div>
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
        domain_value = result["sender_domain"] if result["sender_domain"] else "N/A"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Sender Domain</div>
                <div class="metric-value-small">{domain_value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Risk Visualization")
    render_progress_bar(result["score"], label)

    st.markdown(
        f'<div class="{style_class}">Final Assessment: {label}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("### Triggered Indicators")
    if result["triggered_indicators"]:
        for item in result["triggered_indicators"]:
            st.markdown(
                f'<div class="evidence-card">{item}</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="result-good">No strong suspicious indicators were detected in this email.</div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown("---")
    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">Ready for Analysis</div>
            <div class="panel-subtitle">
                Fill in the email details and run the lightweight detection engine to see the scam risk assessment.
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