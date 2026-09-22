import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

try:
    from .schemas import ClinicalSafetyReport
except ImportError:
    from schemas import ClinicalSafetyReport


load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "outputs/reports"
REPORTS.mkdir(parents=True, exist_ok=True)

DISCLAIMER = (
    "This is an engineering-skill demonstration for a learning project, "
    "not real clinical or regulatory guidance. It must not be used for "
    "medical decision-making."
)

AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT",
    "https://vijayalakshmi-7360-resource.services.ai.azure.com/openai/v1",
)

AZURE_OPENAI_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT",
    "model-router",
)


def build_grounded_prompt(risk_output, retrieved_chunks):
    return f"""
Use ONLY these factual sources.

Module 1 risk output:
{risk_output}

Module 3 retrieved guideline chunks:
{retrieved_chunks}

Safety and grounding rules:

1. Never recommend a dose that contradicts the retrieved guideline text.
2. Never invent any clinical metric, statistic, warning, dose, or guideline
   that is not supported by the retrieved chunks.
3. If the retrieved chunks do not contain enough information, use a
   conservative response and explicitly explain the limitation in
   Reasoning_Steps rather than putting explanatory text into typed fields.

4. Eligible_For_Vaccine MUST be a JSON boolean:
   true or false only.
   NEVER return a sentence, explanation, "undetermined", "unknown",
   or other text in this field.

5. Recommended_Dose_mg MUST be a JSON number.
   NEVER return a sentence, explanation, "not determinable", "unknown",
   or other text in this field.

6. If the available information is insufficient to establish eligibility
   or determine a dose, express that limitation clearly in
   Reasoning_Steps while still returning the required boolean and numeric
   values.

7. FDA_Safety_Warnings_Cited MUST be a JSON array of strings.
   Include all relevant safety warnings that are explicitly supported
   by the retrieved guideline chunks. Do not omit supported warnings.

8. Recommended_Dose_mg must be expressed in milligrams. If the retrieved
   source gives a dose in micrograms, convert micrograms to milligrams
   by dividing by 1000.

9. Do not describe the supplied course reference as an actual FDA or
   regulatory document unless the retrieved text explicitly establishes that.

10. Always include this disclaimer:
    {DISCLAIMER}

Return ONLY valid JSON matching the ClinicalSafetyReport schema.
Do not include Markdown fences, commentary, or additional fields.
""".strip()


def validate_report(payload):
    return ClinicalSafetyReport(**payload)


def _create_llm():
    """
    Create the LangChain LLM client using Microsoft Foundry's
    OpenAI-compatible endpoint.

    Local development keeps the existing Azure CLI / Entra
    DefaultAzureCredential path. Hosted deployments can supply
    an Azure API key through Streamlit Secrets or an environment
    variable.
    """
    azure_api_key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()

    if not azure_api_key:
        try:
            import streamlit as st

            azure_api_key = str(
                st.secrets.get("AZURE_OPENAI_API_KEY", "")
            ).strip()
        except Exception:
            azure_api_key = ""

    if azure_api_key:
        return ChatOpenAI(
            base_url=AZURE_OPENAI_ENDPOINT,
            api_key=azure_api_key,
            model=AZURE_OPENAI_DEPLOYMENT,
            temperature=0,
        )

    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default",
    )

    return ChatOpenAI(
        base_url=AZURE_OPENAI_ENDPOINT,
        api_key=token_provider,
        model=AZURE_OPENAI_DEPLOYMENT,
        temperature=0,
    )


def _parse_json_response(content):
    """
    Convert the LLM response into a Python dictionary.

    The prompt requests plain JSON, but this also safely handles a
    JSON response accidentally wrapped in Markdown code fences.
    """
    text = content.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def generate_report(risk_output, retrieved_chunks):
    """
    Generate a grounded ClinicalSafetyReport using the Azure Foundry
    deployment through LangChain.

    Validation is attempted once. If the first response fails JSON
    parsing or Pydantic validation, one corrective retry is performed.
    """

    llm = _create_llm()
    prompt = build_grounded_prompt(risk_output, retrieved_chunks)

    response = llm.invoke(prompt)

    try:
        payload = _parse_json_response(response.content)
        report = validate_report(payload)
        return report

    except Exception as first_error:
        retry_prompt = f"""
The previous response could not be parsed or validated.

Validation/parsing error:
{first_error}

Generate the ClinicalSafetyReport again.

IMPORTANT:
- Use ONLY the risk output and retrieved guideline chunks below.
- Do not invent clinical information.
- Do not contradict the retrieved guideline text.
- Return ONLY valid JSON.
- Return exactly these five fields:
  Eligible_For_Vaccine
  Recommended_Dose_mg
  Reasoning_Steps
  FDA_Safety_Warnings_Cited
  Disclaimer

- Eligible_For_Vaccine MUST be true or false.
  It MUST NOT contain explanatory text.

- Recommended_Dose_mg MUST be a numeric value in milligrams.
  It MUST NOT contain explanatory text.

- If eligibility or dose cannot be determined from the available
  information, explain that limitation inside Reasoning_Steps.
  Do not put the explanation into Eligible_For_Vaccine or
  Recommended_Dose_mg.

- FDA_Safety_Warnings_Cited MUST be a JSON list of strings.
  Include the relevant warnings supported by the retrieved guideline
  chunks.

- The Disclaimer must contain:
  {DISCLAIMER}

Module 1 risk output:
{risk_output}

Module 3 retrieved guideline chunks:
{retrieved_chunks}
""".strip()

        retry_response = llm.invoke(retry_prompt)
        retry_payload = _parse_json_response(retry_response.content)

        return validate_report(retry_payload)


def save_report(report, stem="clinical_safety_report"):
    json_path = REPORTS / f"{stem}.json"
    markdown_path = REPORTS / f"{stem}.md"

    json_path.write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )

    markdown_path.write_text(
        "# Clinical Safety Report\n\n"
        + report.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return json_path, markdown_path