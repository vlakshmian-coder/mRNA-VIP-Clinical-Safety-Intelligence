from pathlib import Path
from .schemas import ClinicalSafetyReport
ROOT=Path(__file__).resolve().parents[1]; REPORTS=ROOT/"outputs/reports"; REPORTS.mkdir(parents=True,exist_ok=True)
DISCLAIMER="This is an engineering-skill demonstration for a learning project, not real clinical or regulatory guidance. It must not be used for medical decision-making."
def build_grounded_prompt(risk_output,retrieved_chunks): return f"Use ONLY these factual sources. Module 1 risk output: {risk_output}. Module 3 retrieved guideline chunks: {retrieved_chunks}. Return exactly the five required ClinicalSafetyReport fields. Disclaimer: {DISCLAIMER}"
def validate_report(payload): return ClinicalSafetyReport(**payload)
def save_report(report,stem="clinical_safety_report"):
 (REPORTS/f"{stem}.json").write_text(report.model_dump_json(indent=2),encoding="utf-8"); (REPORTS/f"{stem}.md").write_text("# Clinical Safety Report\n\n"+report.model_dump_json(indent=2),encoding="utf-8")
