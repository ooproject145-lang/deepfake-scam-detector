import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="Deepfake Scam Detector",
    page_icon="🛡️",
    layout="wide",
)

def load_css():
    css_file = Path("assets/styles.css")
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

with st.sidebar:
    st.markdown("## 🛡️ Scam Detection System")
    st.caption("Email & Voice Protection")
    st.markdown("---")
    st.markdown("### Navigation")
    st.write("Use the pages on the left")
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
        <div class="hero-title">Deepfake Email and Voice Scam Detection System</div>
        <div class="hero-text">
            A lightweight cybersecurity system designed to detect AI-generated scams
            using both text and voice analysis.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Get Started")
st.markdown(
    """
- Go to **Email Analyzer**
- Go to **Voice Analyzer**
- Run detection and view results
"""
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