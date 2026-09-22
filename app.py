
import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pipeline import run_pipeline  # noqa: E402

DISCLAIMER = (
    "Student engineering project for demonstration and portfolio purposes only. "
    "This is not real clinical guidance and must not be used for medical decisions."
)

st.set_page_config(
    page_title="mRNA-VIP | Clinical Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --navy:#071b2d; --navy2:#0d3049; --teal:#17a996; --cyan:#49c7e8;
  --ink:#102b43; --muted:#718396; --line:#dce7ee; --bg:#f4f8fb;
}

html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp {
  background:
    radial-gradient(circle at 90% 0%, rgba(73,199,232,.10), transparent 25%),
    radial-gradient(circle at 10% 25%, rgba(23,169,150,.07), transparent 23%),
    var(--bg);
}
.block-container { max-width:1500px; padding:1.15rem 2.2rem 3rem; }

/* Sidebar */
[data-testid="stSidebar"] {
  background:linear-gradient(180deg,#06192b 0%,#0b2941 100%);
  border-right:1px solid rgba(255,255,255,.08);
}
[data-testid="stSidebar"] * { color:#eaf6fb !important; }
[data-testid="stSidebar"] label { font-weight:600; font-size:.82rem; }
[data-testid="stSidebar"] input {
  color:#102b43 !important; background:#ffffff !important;
  -webkit-text-fill-color:#102b43 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] * {
  color:#102b43 !important; background:#ffffff !important;
}
[data-testid="stSidebar"] .stButton button {
  border:0; border-radius:12px; font-weight:700;
  background:linear-gradient(100deg,#16aa98,#3e9ff2);
  color:white !important; box-shadow:0 10px 24px rgba(0,0,0,.22);
}
.sidebar-brand {
  padding:4px 0 18px; border-bottom:1px solid rgba(255,255,255,.13);
  margin-bottom:18px;
}
.sidebar-brand .mini { color:#74d7d0; font-size:.72rem; font-weight:800; letter-spacing:1.5px; }
.sidebar-brand .big { font-family:'Space Grotesk'; font-size:1.65rem; font-weight:700; margin-top:4px; }

/* Hero */
.hero {
  min-height:270px; border-radius:28px; padding:34px 38px;
  background:
    radial-gradient(circle at 88% 8%, rgba(73,199,232,.30), transparent 24%),
    radial-gradient(circle at 74% 105%, rgba(23,169,150,.28), transparent 32%),
    linear-gradient(125deg,#061b2e 0%,#0b304a 58%,#0b5b66 100%);
  color:#fff; position:relative; overflow:hidden;
  box-shadow:0 20px 50px rgba(6,27,46,.17);
}
.hero:before {
  content:""; position:absolute; right:-80px; top:-110px; width:350px; height:350px;
  border:1px solid rgba(255,255,255,.14); border-radius:50%;
  box-shadow:0 0 0 45px rgba(255,255,255,.025),0 0 0 90px rgba(255,255,255,.018);
}
.hero-kicker { font-size:.73rem; letter-spacing:2px; font-weight:800; color:#6ce1d2; }
.hero-title { font-family:'Space Grotesk'; font-size:3.35rem; line-height:1; font-weight:700; letter-spacing:-2px; margin-top:12px; }
.hero-sub { font-size:1.08rem; color:#d6e9f1; margin-top:12px; max-width:650px; }
.hero-chips { display:flex; gap:8px; flex-wrap:wrap; margin-top:22px; }
.chip { padding:7px 12px; border:1px solid rgba(255,255,255,.18); border-radius:999px; background:rgba(255,255,255,.08); font-size:.72rem; font-weight:700; }

.notice {
  margin:16px 0 18px; padding:12px 16px; border-radius:12px;
  background:#fff8eb; border:1px solid #f0d6a9; border-left:5px solid #e39a4b;
  color:#6e4219; font-size:.82rem;
}

/* Pipeline */
.pipeline { display:flex; gap:7px; margin:18px 0 22px; }
.pstep {
  flex:1; background:#fff; border:1px solid var(--line); border-radius:15px;
  padding:14px 10px; box-shadow:0 7px 22px rgba(16,43,67,.045);
}
.pstep .n { color:#19a796; font-size:.68rem; font-weight:800; letter-spacing:1px; }
.pstep .t { color:var(--ink); font-weight:800; margin-top:5px; font-size:.91rem; }
.pstep .d { color:#8191a1; font-size:.68rem; margin-top:4px; }
.arrow { align-self:center; color:#9aabba; font-size:1.1rem; }

/* Section */
.eyebrow { color:#1a9f91; font-size:.69rem; font-weight:800; letter-spacing:1.6px; text-transform:uppercase; }
.heading { color:var(--ink); font-family:'Space Grotesk'; font-size:1.45rem; font-weight:700; margin-top:4px; }
.caption { color:var(--muted); font-size:.82rem; margin:3px 0 14px; }

/* Input preview */
.profile {
  background:#fff; border:1px solid var(--line); border-radius:18px; padding:18px;
  box-shadow:0 8px 25px rgba(16,43,67,.05);
}
.profile-label { color:#7a8b9b; font-size:.68rem; text-transform:uppercase; font-weight:800; letter-spacing:.7px; }
.profile-value { color:var(--ink); font-size:1rem; font-weight:700; margin-top:5px; }

/* Results */
.kpi {
  background:#fff; border:1px solid var(--line); border-radius:18px; padding:19px;
  box-shadow:0 8px 25px rgba(16,43,67,.055); min-height:125px;
}
.kpi-label { color:#7b8c9d; font-size:.67rem; font-weight:800; letter-spacing:1px; text-transform:uppercase; }
.kpi-value { color:var(--ink); font-family:'Space Grotesk'; font-size:1.72rem; font-weight:700; margin-top:8px; }
.kpi-note { color:#8a99a8; font-size:.71rem; margin-top:4px; }
.good { color:#168a76 !important; } .warn { color:#b85a3d !important; }

.evidence {
  background:#fff; border:1px solid var(--line); border-radius:15px; padding:16px 18px;
  margin:9px 0; box-shadow:0 5px 18px rgba(16,43,67,.04);
}
.evtag { color:#1a9f91; font-size:.65rem; font-weight:800; letter-spacing:1px; text-transform:uppercase; margin-bottom:7px; }

.report {
  background:linear-gradient(145deg,#fff,#f1faf8); border:1px solid #d7eae6;
  border-radius:20px; padding:22px; box-shadow:0 10px 28px rgba(16,43,67,.055);
}
.report-title { font-family:'Space Grotesk'; font-size:1.2rem; font-weight:700; color:var(--ink); }
.pill { display:inline-block; padding:5px 10px; border-radius:999px; font-size:.7rem; font-weight:800; }
.pill-green { background:#e3f6ef; color:#16735f; } .pill-red { background:#fae8e4; color:#984634; }

.tech {
  background:#071b2d; color:#d7e8f2; border-radius:18px; padding:20px;
  font-size:.78rem; line-height:1.75; box-shadow:0 12px 28px rgba(6,27,45,.12);
}
.footer { text-align:center; color:#8b9aa8; font-size:.7rem; margin-top:28px; }
div[data-testid="stTabs"] button { font-weight:700; }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
      <div class="mini">AI CLINICAL INTELLIGENCE</div>
      <div class="big">🧬 mRNA-VIP</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Patient Assessment")
    st.caption("Use the pre-filled demonstration profile for the portfolio walkthrough.")

    patient_id = st.text_input("Patient ID", "DEMO-001")
    age = st.number_input("Age", 18, 100, 50, 1)
    biomarker = st.number_input("Biomarker Level", 0.0, 100.0, 5.0, 0.1)
    pre_existing = st.number_input("Pre-existing Conditions", 0, 20, 1, 1)
    dose_mcg = st.number_input("Candidate Vaccine Dose (mcg)", 1.0, 200.0, 50.0, 0.5)
    prior_reaction = st.selectbox("Prior Reaction History", ["None reported", "Mild", "Moderate"])
    sequence = st.text_input("mRNA Sequence", "ACGUACGUACGGCUA").strip().upper()

    st.markdown("---")
    run = st.button("🚀  Run AI Safety Assessment", use_container_width=True)
    if st.button("↻ Reset Demo", use_container_width=True):
        st.session_state.pop("mRNA_vip_result", None)
        st.rerun()

# Hero
st.markdown("""
<div class="hero">
  <div class="hero-kicker">END-TO-END AI SAFETY INTELLIGENCE</div>
  <div class="hero-title">🧬 mRNA-VIP</div>
  <div class="hero-sub">Clinical Safety &amp; Dosage Intelligence Platform</div>
  <div class="hero-chips">
    <span class="chip">ML Risk Engine</span>
    <span class="chip">Self-Attention</span>
    <span class="chip">ChromaDB RAG</span>
    <span class="chip">Structured LLM</span>
    <span class="chip">Explainable Output</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="notice"><strong>⚠ Safety boundary:</strong> {DISCLAIMER}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="pipeline">
  <div class="pstep"><div class="n">01</div><div class="t">ML Risk</div><div class="d">Patient risk scoring</div></div>
  <div class="arrow">→</div>
  <div class="pstep"><div class="n">02</div><div class="t">Attention</div><div class="d">Sequence analysis</div></div>
  <div class="arrow">→</div>
  <div class="pstep"><div class="n">03</div><div class="t">RAG</div><div class="d">Evidence retrieval</div></div>
  <div class="arrow">→</div>
  <div class="pstep"><div class="n">04</div><div class="t">LLM</div><div class="d">Grounded report</div></div>
  <div class="arrow">→</div>
  <div class="pstep"><div class="n">05</div><div class="t">Output</div><div class="d">Validated artifacts</div></div>
</div>
""", unsafe_allow_html=True)

# Main profile preview
st.markdown('<div class="eyebrow">Demo Profile</div><div class="heading">Patient context</div><div class="caption">The sidebar controls the live assessment. This summary makes the demo state visible on the main canvas.</div>', unsafe_allow_html=True)

cols = st.columns(6)
items = [
    ("Patient", patient_id),
    ("Age", age),
    ("Biomarker", f"{biomarker:g}"),
    ("Conditions", pre_existing),
    ("Candidate Dose", f"{dose_mcg:g} µg"),
    ("mRNA", f"{len(sequence)} bases"),
]
for col, (label, value) in zip(cols, items):
    with col:
        st.markdown(f'<div class="profile"><div class="profile-label">{label}</div><div class="profile-value">{value}</div></div>', unsafe_allow_html=True)

# Execute
if run:
    if not sequence:
        st.error("Please enter an mRNA sequence.")
        st.stop()
    if len(sequence) < 5 or len(sequence) > 50:
        st.error("mRNA sequence must contain between 5 and 50 bases.")
        st.stop()
    invalid = sorted(set(sequence) - set("ACGU"))
    if invalid:
        st.error(f"Invalid sequence character(s): {', '.join(invalid)}. Use A, C, G and U only.")
        st.stop()

    patient = {
        "Patient_ID": patient_id,
        "Age": age,
        "Biomarker_Level": biomarker,
        "Pre_Existing_Conditions": pre_existing,
        "Vaccine_Dose_mcg": dose_mcg,
        "Prior_Reaction_History": None if prior_reaction == "None reported" else prior_reaction,
    }

    with st.status("Running the mRNA-VIP intelligence pipeline...", expanded=True) as status:
        try:
            result = run_pipeline(patient, sequence)
            status.update(label="✓ Assessment complete", state="complete")
        except Exception as exc:
            status.update(label="Assessment failed", state="error")
            st.error("The underlying pipeline returned an error. The UI is intact.")
            st.exception(exc)
            st.stop()
    st.session_state["mRNA_vip_result"] = result

result = st.session_state.get("mRNA_vip_result")

if not result:
    st.markdown("""
    <div class="evidence" style="margin-top:18px;">
      <div class="eyebrow">Ready</div>
      <div style="font-family:'Space Grotesk';font-size:1.15rem;font-weight:700;color:#102b43;margin-top:5px;">
        Run the assessment to reveal the AI-generated safety intelligence.
      </div>
      <div style="color:#718396;font-size:.82rem;margin-top:6px;">
        The live result view will surface the risk score, molecular attention map,
        retrieved evidence and structured safety report.
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    risk = result.get("risk", {})
    attention = result.get("attention", {})
    retrieval = result.get("retrieval", {})
    report = result.get("report", {})
  
    if hasattr(report, "model_dump"):
        report = report.model_dump()
    elif not isinstance(report, dict):
        report = {}

    paths = result.get("report_paths", {})
    latency = result.get("latency_seconds", result.get("latency"))

    risk_label = risk.get("risk_label", risk.get("label", "Unknown"))
    probability = risk.get("risk_probability", risk.get("probability", 0))
    model_name = risk.get("model_name", "Risk model")
    try:
        pct = float(probability) * 100
    except Exception:
        pct = 0.0

    recommended = report.get("Recommended_Dose_mg", report.get("recommended_dose_mg", "—"))

    st.markdown('<div class="eyebrow">Assessment Result</div><div class="heading">AI Safety Intelligence</div><div class="caption">End-to-end output from the current demonstration run.</div>', unsafe_allow_html=True)

    k = st.columns(4)
    with k[0]:
        cls = "warn" if str(risk_label).lower() == "high" else "good"
        st.markdown(f'<div class="kpi"><div class="kpi-label">Risk Classification</div><div class="kpi-value {cls}">{risk_label}</div><div class="kpi-note">{model_name}</div></div>', unsafe_allow_html=True)
    with k[1]:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Risk Probability</div><div class="kpi-value">{pct:.1f}%</div><div class="kpi-note">Predicted reaction risk</div></div>', unsafe_allow_html=True)
    with k[2]:
        st.markdown(f'<div class="kpi"><div class="kpi-label">Recommended Dose</div><div class="kpi-value">{recommended} mg</div><div class="kpi-note">Validated structured output</div></div>', unsafe_allow_html=True)
    with k[3]:
        lt = f"{float(latency):.2f}s" if latency is not None else "—"
        st.markdown(f'<div class="kpi"><div class="kpi-label">Pipeline Latency</div><div class="kpi-value">{lt}</div><div class="kpi-note">End-to-end execution</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["🧬 Attention Analysis", "📚 Evidence Grounding", "🤖 Safety Report", "⚙️ Architecture"])

    with t1:
        st.markdown('<div class="eyebrow">Molecular Analysis</div><div class="heading">Self-Attention Map</div><div class="caption">Attention weights generated for the supplied mRNA sequence.</div>', unsafe_allow_html=True)
        attention_path = attention.get("heatmap_path") or attention.get("figure_path") or attention.get("path")
        if attention_path and Path(attention_path).exists():
            st.image(attention_path, caption=f"Self-attention heatmap • {sequence}", use_container_width=True)
        else:
            st.info("The attention heatmap was not returned by the pipeline.")

    with t2:
        st.markdown('<div class="eyebrow">Retrieval-Augmented Generation</div><div class="heading">Evidence Grounding</div><div class="caption">Retrieved course-reference chunks provided to the structured report generator.</div>', unsafe_allow_html=True)
        chunks = retrieval.get("chunks", []) if isinstance(retrieval, dict) else retrieval
        if chunks:
            for i, chunk in enumerate(chunks, 1):
                safe = str(chunk).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
                st.markdown(f'<div class="evidence"><div class="evtag">Evidence {i}</div>{safe}</div>', unsafe_allow_html=True)
        else:
            st.info("No retrieved evidence was returned.")

    with t3:
        st.markdown('<div class="eyebrow">Structured Output</div><div class="heading">Clinical Safety Report</div><div class="caption">Schema-oriented report produced from the risk result and retrieved evidence.</div>', unsafe_allow_html=True)
        eligible = report.get("Eligible_For_Vaccine", report.get("eligible_for_vaccine"))
        reasoning = report.get("Reasoning_Steps", report.get("reasoning_steps", []))
        warnings = report.get("FDA_Safety_Warnings_Cited", report.get("fda_safety_warnings_cited", []))
        rep_disc = report.get("Disclaimer", DISCLAIMER)
        if eligible is True:
            pill = '<span class="pill pill-green">ELIGIBLE</span>'
        elif eligible is False:
            pill = '<span class="pill pill-red">NOT ELIGIBLE</span>'
        else:
            pill = '<span class="pill pill-red">NOT SPECIFIED</span>'

        st.markdown(f"""
        <div class="report">
          <div class="report-title">Safety assessment</div>
          <div style="margin-top:14px;"><b>Eligibility</b> &nbsp; {pill}</div>
          <div style="margin-top:16px;color:#7b8c9d;font-size:.68rem;font-weight:800;letter-spacing:1px;">RECOMMENDED DOSE</div>
          <div style="font-family:'Space Grotesk';font-size:1.8rem;font-weight:700;color:#102b43;margin-top:3px;">{recommended} mg</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Reasoning")
        if reasoning:
            for i, item in enumerate(reasoning, 1):
                st.markdown(f"**{i}.** {item}")
        else:
            st.info("No reasoning steps returned.")

        st.markdown("#### Safety Warnings Cited")
        if warnings:
            for warning in warnings:
                st.warning(str(warning))
        else:
            st.info("No warnings returned.")

        st.info(rep_disc or DISCLAIMER)
        st.download_button(
            "⬇️ Download Structured JSON",
            data=json.dumps(report, indent=2, ensure_ascii=False, default=str),
            file_name=f"{patient_id}_clinical_safety_report.json",
            mime="application/json",
        )

    with t4:
        st.markdown('<div class="eyebrow">Engineering Architecture</div><div class="heading">How mRNA-VIP works</div><div class="caption">The presentation layer sits on top of the existing end-to-end project pipeline.</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="tech">
        <b>1. Patient Data</b> → structured profile and mRNA sequence<br>
        <b>2. ML Risk Engine</b> → classification and probability<br>
        <b>3. Self-Attention</b> → sequence-level attention visualization<br>
        <b>4. ChromaDB RAG</b> → grounded safety-reference retrieval<br>
        <b>5. Structured LLM</b> → report generation through the schema layer<br>
        <b>6. Output</b> → JSON + Markdown portfolio artifacts<br><br>
        <b>Core stack:</b> Python • Pandas • Scikit-learn • PyTorch • ChromaDB • LangChain • Streamlit
        </div>
        """, unsafe_allow_html=True)
        if paths:
            st.markdown("#### Generated Artifacts")
            st.json(paths)

st.markdown('<div class="footer">mRNA-VIP • Clinical Safety & Dosage Intelligence • Student Engineering Portfolio Project</div>', unsafe_allow_html=True)
