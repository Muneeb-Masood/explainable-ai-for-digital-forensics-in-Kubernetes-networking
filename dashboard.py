import streamlit as st
import subprocess

st.set_page_config(page_title="Explainable AI for Digital Forensics in Kubernetes Networking", layout="wide")

# --- Custom CSS for dark/cyber theme and attack vibes ---
st.markdown(
    """
    <style>
    body, .stApp {
        background: #121212 !important;
    }
    .attack-banner {
        background: #1e1e1e;
        color: #f5f5f5;
        font-size: 2.3rem;
        font-weight: bold;
        padding: 1.2rem 0.5rem 1.2rem 1.5rem;
        border-radius: 0.9rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 24px #d7263d55;
        letter-spacing: 2px;
        border-left: 10px solid #d7263d;
        border-bottom: 3px solid #d7263d;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .attack-banner .icon {
        font-size: 2.5rem;
        margin-right: 0.7rem;
    }
    .section-divider {
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #d7263d 0%, #1e1e1e 100%);
        margin: 2rem 0 2rem 0;
        border-radius: 2px;
        box-shadow: 0 0 8px #d7263d44;
    }
    .cyber-box {
        background: #1e1e1e;
        border: 1.5px solid #232323;
        border-radius: 0.7rem;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        color: #f5f5f5;
        font-family: 'Consolas', 'Fira Mono', 'Menlo', monospace;
        font-size: 1.13rem;
        box-shadow: 0 0 12px #23232322;
    }
    .status-card {
        background: #1e1e1e;
        border-radius: 1rem;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 0 16px #23232344;
        color: #f5f5f5;
        border: 2px solid #232323;
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
    }
    .status-title {
        font-size: 1.3rem;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .status-healthy {
        color: #00e676 !important;
        font-weight: bold;
    }
    .status-alert {
        color: #d7263d !important;
        font-weight: bold;
    }
    .stDataFrame, .stTable {
        background: #232323 !important;
        color: #f5f5f5 !important;
        border-radius: 0.5rem !important;
        border: 1.5px solid #232323 !important;
        box-shadow: 0 0 8px #23232322;
    }
    .stCode, .st-cd, pre, code {
        background: #181818 !important;
        color: #f5f5f5 !important;
        border-radius: 0.5rem !important;
        border: 1.5px solid #232323 !important;
        font-family: 'Fira Mono', 'Consolas', 'Menlo', monospace !important;
        font-size: 1.08rem !important;
        box-shadow: 0 0 8px #23232322;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="attack-banner"><span class="icon">🛡️</span>Explainable AI for Digital Forensics in Kubernetes Networking</div>', unsafe_allow_html=True)

st.markdown("""
<div class="cyber-box">
<b>Welcome to the <span style='color:#d7263d;'>Explainable AI for Digital Forensics in Kubernetes Networking</span> dashboard.</b><br>
<span style='color:#d7263d;'>🔍 Analyze, visualize, and explain security events and network forensics</span> in your Kubernetes cluster.<br>
<b>All forensic results and explainable AI insights in one place.</b>
</div>
<hr class="section-divider" />
""", unsafe_allow_html=True)

# --- Read-only Dashboard ---

st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
st.markdown('<h2 style="color:#d7263d;letter-spacing:1px;">🛰️ Live Cluster Status</h2>', unsafe_allow_html=True)
col5, col6 = st.columns(2)

import pandas as pd

with col5:
    st.markdown('<div style="color:#ff003c;font-size:1.3rem;font-weight:bold;">📊 HPA Status</div>', unsafe_allow_html=True)
    hpa_status = subprocess.getoutput("kubectl get hpa php-apache -o wide")
    st.code(hpa_status)
    hpa_lines = hpa_status.strip().split("\n")
    if len(hpa_lines) > 1:
        hpa_cols = hpa_lines[0].split()
        hpa_data = [line.split() for line in hpa_lines[1:]]
        try:
            hpa_df = pd.DataFrame(hpa_data, columns=hpa_cols)
            st.markdown('<div class="cyber-box">HPA Table</div>', unsafe_allow_html=True)
            st.dataframe(hpa_df)
        except Exception as e:
            st.warning(f"Could not parse HPA status for table. Error: {e}")

    st.markdown('<div style="color:#ff003c;font-size:1.3rem;font-weight:bold;">📦 Pods</div>', unsafe_allow_html=True)
    pods = subprocess.getoutput("kubectl get pods -o wide")
    st.code(pods)
    pod_lines = pods.strip().split("\n")
    if len(pod_lines) > 1:
        pod_cols = pod_lines[0].split()
        pod_data = [line.split() for line in pod_lines[1:]]
        try:
            pod_df = pd.DataFrame(pod_data, columns=pod_cols)
            st.markdown('<div class="cyber-box">Pod Table</div>', unsafe_allow_html=True)
            st.dataframe(pod_df)
        except Exception:
            st.info("Could not parse pod status for table.")

with col6:
    st.markdown('<div style="color:#ff003c;font-size:1.3rem;font-weight:bold;">📈 Pod Metrics</div>', unsafe_allow_html=True)
    pod_metrics = subprocess.getoutput("kubectl top pods")
    st.code(pod_metrics)
    st.markdown('<div style="color:#ff003c;font-size:1.3rem;font-weight:bold;">🌐 Service</div>', unsafe_allow_html=True)
    svc = subprocess.getoutput("kubectl get svc php-apache")
    st.code(svc)

# --- SHAP/AI Images Grid with Show/Hide Toggle ---
with col5:
    st.markdown('<div class="status-card"><span class="status-title">📊 HPA Status</span>', unsafe_allow_html=True)
    hpa_status = subprocess.getoutput("kubectl get hpa php-apache -o wide")
    st.code(hpa_status)
    hpa_lines = hpa_status.strip().split("\n")
    if len(hpa_lines) > 1:
        hpa_cols = hpa_lines[0].split()
        hpa_data = [line.split() for line in hpa_lines[1:]]
        try:
            hpa_df = pd.DataFrame(hpa_data, columns=hpa_cols)
            st.dataframe(hpa_df)
            # Status color
            if any('True' in row for row in hpa_data):
                st.markdown('<span class="status-healthy">🟢 Healthy</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-alert">🔴 Alert</span>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<span class="status-alert">Could not parse HPA status for table. Error: {e}</span>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="status-card"><span class="status-title">📦 Pods</span>', unsafe_allow_html=True)
    pods = subprocess.getoutput("kubectl get pods -o wide")
    st.code(pods)
    pod_lines = pods.strip().split("\n")
    if len(pod_lines) > 1:
        pod_cols = pod_lines[0].split()
        pod_data = [line.split() for line in pod_lines[1:]]
        try:
            pod_df = pd.DataFrame(pod_data, columns=pod_cols)
            st.dataframe(pod_df)
            # Status color
            if all('Running' in row for row in pod_data):
                st.markdown('<span class="status-healthy">🟢 All Running</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-alert">🔴 Pod Issue</span>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<span class="status-alert">Could not parse pod status for table. Error: {e}</span>', unsafe_allow_html=True)



# --- SHAP/AI Images Grid with Show/Hide Toggle ---
import os
import glob
from PIL import Image

st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
st.markdown('<h2 style="color:#d7263d;letter-spacing:1px;">🖼️ SHAP & AI Analysis Images</h2>', unsafe_allow_html=True)
show_images = st.toggle("Show Analysis Images Grid", value=False)
img_dir = "explainable-ai/outputs/"
img_types = ["*.png", "*.jpg", "*.jpeg"]
img_files = []
if show_images:
    for t in img_types:
        img_files.extend(glob.glob(os.path.join(img_dir, t)))
    if img_files:
        cols = st.columns(3)
        for idx, img_path in enumerate(img_files):
            with cols[idx % 3]:
                st.image(Image.open(img_path), caption=os.path.basename(img_path), use_container_width=True)
    else:
        st.warning("No analysis images are present.")

# --- Gemini Forensic Analysis Report Show/Hide Toggle ---
st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
st.markdown('<h2 style="color:#d7263d;letter-spacing:1px;">📜 AI-Generated Forensic Report</h2>', unsafe_allow_html=True)
gemini_report_path = os.path.join(img_dir, "Gemini_Forensic_Analysis.md")
if os.path.exists(gemini_report_path):
    show_gemini = st.toggle("Show AI-Generated Forensic Report", value=False)
    if show_gemini:
        with open(gemini_report_path, "r", encoding="utf-8") as f:
            report_content = f.read()
        st.markdown('<div class="cyber-box">'+report_content+'</div>', unsafe_allow_html=True)
else:
    st.info("AI-generated forensic report not found.")

st.markdown('<hr class="section-divider" />', unsafe_allow_html=True)
st.caption("Made with Streamlit. For best results, run this dashboard on the same machine as your Kubernetes cluster.")
