"""
mRNA-VIP end-to-end orchestrator.

This module connects the existing project modules without replacing them:
ML risk model -> self-attention -> ChromaDB RAG -> structured report.

The actual LLM configuration remains in src/report_generator.py.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from attention import encode_sequence, plot_attention, self_attention  # noqa: E402
from data_pipeline import CATEGORICAL_COL, NUMERIC_COLS, clean_data  # noqa: E402
from rag_index import build_index, query_guidelines  # noqa: E402
from report_generator import generate_report  # noqa: E402


MODEL_PATH = ROOT / "outputs" / "risk_model.joblib"
PATIENT_DATA_PATH = ROOT / "data" / "patient_records.csv"
REPORTS_DIR = ROOT / "outputs" / "reports"
FIGURES_DIR = ROOT / "outputs" / "figures"

DISCLAIMER = (
    "Student engineering project output — not real clinical guidance. "
    "Do not use this output for real-world medical decisions."
)


def _load_risk_artifact() -> dict[str, Any]:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Risk model not found at {MODEL_PATH}. Run risk_model.py first."
        )
    return joblib.load(MODEL_PATH)


def predict_risk(patient: dict[str, Any]) -> dict[str, Any]:
    """Score one patient using the exact preprocessing objects saved with the model."""
    artifact = _load_risk_artifact()
    model = artifact["model"]
    scaler = artifact["scaler"]
    encoder = artifact["encoder"]
    feature_columns = artifact["feature_columns"]

    reference = pd.read_csv(PATIENT_DATA_PATH)
    row = pd.DataFrame([patient])

    # Match training-time cleaning: numeric medians and categorical mode.
    row = clean_data(row, reference_df=reference)

    # Preserve the exact feature construction used by data_pipeline.prepare_features().
    numeric = row[NUMERIC_COLS].astype(float).copy()
    numeric.loc[:, NUMERIC_COLS] = scaler.transform(numeric)

    categorical = encoder.transform(row[CATEGORICAL_COL]).astype(float)
    features = numeric.copy()
    features[CATEGORICAL_COL] = categorical
    features["Pre_Existing_Conditions"] = row["Pre_Existing_Conditions"].to_numpy()
    features = features[feature_columns]

    predicted = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]

    # The project target is Reaction_Score 0/1.
    class_to_probability = {
        int(cls): float(prob)
        for cls, prob in zip(model.classes_, probabilities)
    }
    risk_probability = class_to_probability.get(1, float(max(probabilities)))
    risk_label = "High" if predicted == 1 else "Low"

    return {
        "risk_label": risk_label,
        "risk_probability": risk_probability,
        "prediction": predicted,
        "model_name": artifact.get("model_name", type(model).__name__),
    }


def run_attention(sequence: str) -> dict[str, Any]:
    """Run the existing toy self-attention module and save its heatmap."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    sequence = sequence.strip().upper()
    if not sequence:
        raise ValueError("Sequence cannot be empty.")
    invalid = sorted(set(sequence) - set("ACGU"))
    if invalid:
        raise ValueError(f"Invalid nucleotide(s): {', '.join(invalid)}")

    X = encode_sequence(sequence)
    weights, output = self_attention(X)

    heatmap_path = FIGURES_DIR / "attention_heatmap.png"
    plot_attention(weights, sequence, str(heatmap_path))

    return {
        "sequence": sequence,
        "embedding_shape": tuple(X.shape),
        "attention_shape": tuple(weights.shape),
        "attention_output_shape": tuple(output.shape),
        "attention_weights": weights,
        "heatmap_path": heatmap_path,
    }


def ensure_rag_index() -> None:
    """Create the persistent local ChromaDB index only when it is absent."""
    import chromadb

    db_path = ROOT / "outputs" / "chroma_db"
    if not db_path.exists():
        build_index()
        return

    client = chromadb.PersistentClient(path=str(db_path))
    try:
        client.get_collection("mrna_safety_guidelines")
    except Exception:
        build_index()


def retrieve_guidelines(patient: dict[str, Any], risk: dict[str, Any]) -> dict[str, Any]:
    """Retrieve guideline text relevant to the patient profile and model result."""
    ensure_rag_index()

    question = (
        f"Patient age {patient['Age']}, biomarker level {patient['Biomarker_Level']}, "
        f"pre-existing conditions {patient['Pre_Existing_Conditions']}, "
        f"candidate vaccine dose {patient['Vaccine_Dose_mcg']} micrograms, "
        f"prior reaction history {patient.get('Prior_Reaction_History', '') or 'none reported'}, "
        f"predicted reaction risk {risk['risk_label']} with probability "
        f"{risk['risk_probability']:.2f}. What safety, eligibility, dose, "
        f"contraindication, warning, and secondary-review guidance applies?"
    )

    return query_guidelines(question, k=3)


def _patient_summary(patient: dict[str, Any]) -> str:
    return (
        f"Age: {patient['Age']}; "
        f"Biomarker_Level: {patient['Biomarker_Level']}; "
        f"Pre_Existing_Conditions: {patient['Pre_Existing_Conditions']}; "
        f"Vaccine_Dose_mcg: {patient['Vaccine_Dose_mcg']}; "
        f"Prior_Reaction_History: {patient.get('Prior_Reaction_History') or 'None reported'}."
    )


def _save_report(report: Any, stem: str) -> tuple[Path, Path]:
    """Persist a validated Pydantic report as JSON and readable Markdown."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    if hasattr(report, "model_dump"):
        data = report.model_dump()
    elif isinstance(report, dict):
        data = report
    else:
        raise TypeError("Report must be a Pydantic model or dictionary.")

    # Enforce the visible project disclaimer at persistence time as a final guard.
    data["Disclaimer"] = DISCLAIMER

    json_path = REPORTS_DIR / f"{stem}.json"
    md_path = REPORTS_DIR / f"{stem}.md"

    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = ["# mRNA-VIP Clinical Safety Report", ""]
    for key, value in data.items():
        title = key.replace("_", " ")
        if isinstance(value, list):
            lines.append(f"## {title}")
            lines.extend(f"- {item}" for item in value)
        else:
            lines.append(f"## {title}")
            lines.append(str(value))
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path


def run_pipeline(patient: dict[str, Any], sequence: str) -> dict[str, Any]:
    """Run the complete local pipeline and return UI-ready results."""
    started = time.perf_counter()

    risk = predict_risk(patient)
    attention = run_attention(sequence)
    retrieval = retrieve_guidelines(patient, risk)

    chunks = retrieval.get("chunks", [])
    if not chunks:
        raise RuntimeError("RAG returned no guideline chunks; report generation stopped.")

    report = generate_report(
    risk_output=risk,
    retrieved_chunks=chunks,
)

    # Save locally in the required Week 4 JSON + Markdown pair.
    stamp = time.strftime("%Y%m%d_%H%M%S")
    json_path, md_path = _save_report(report, f"clinical_safety_report_{stamp}")

    return {
        "risk": risk,
        "attention": attention,
        "retrieval": retrieval,
        "report": report,
        "report_json": json_path,
        "report_markdown": md_path,
        "total_latency_seconds": time.perf_counter() - started,
    }
