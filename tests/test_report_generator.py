import pytest

from src.report_generator import build_grounded_prompt, validate_report
from src.schemas import ClinicalSafetyReport


def test_grounded_prompt_contains_required_safety_constraints():
    prompt = build_grounded_prompt(
        risk_output={"risk_score": 0.72, "risk_band": "High"},
        retrieved_chunks=[
            "Common dose range in the course reference: 25-100 micrograms.",
            "More than 100 micrograms requires secondary clinician review.",
        ],
    )

    assert "Use ONLY these factual sources" in prompt
    assert "invent" in prompt.lower()
    assert "not real clinical or regulatory guidance" in prompt
    assert "25-100 micrograms" in prompt


def test_validate_report_accepts_valid_structured_report():
    payload = {
        "Eligible_For_Vaccine": True,
        "Recommended_Dose_mg": 0.05,
        "Reasoning_Steps": [
            "Retrieved course-reference text supports the selected dose.",
            "No conflicting retrieved guidance was supplied.",
        ],
        "FDA_Safety_Warnings_Cited": [],
        "Disclaimer": (
            "This is an engineering-skill demonstration for a learning project, "
            "not real clinical or regulatory guidance. It must not be used for "
            "medical decision-making."
        ),
    }

    report = validate_report(payload)

    assert isinstance(report, ClinicalSafetyReport)
    assert report.Eligible_For_Vaccine is True
    assert report.Recommended_Dose_mg == 0.05


def test_validate_report_rejects_missing_required_field():
    payload = {
        "Eligible_For_Vaccine": True,
        "Recommended_Dose_mg": 0.05,
        "Reasoning_Steps": ["Evidence-based reasoning."],
        "FDA_Safety_Warnings_Cited": [],
    }

    with pytest.raises(Exception):
        validate_report(payload)