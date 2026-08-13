"""
SelfHealSQL: AI Diagnostic Agent (Gemini version)
Reads failure JSON files from logs/ (written by runner.py when a query fails),
sends the failure details to the free Gemini API, and saves a structured diagnosis.

Before running:
    pip install google-genai python-dotenv

Setup:
    1. Get a free API key at https://aistudio.google.com (click "Get API key", no card needed).
    2. Create a file named .env in this project folder with this line:
           GEMINI_API_KEY=your-real-key-here
    3. Add .env to your .gitignore so it never gets committed.
"""

import os
import json
import glob
from datetime import datetime

from dotenv import load_dotenv
from google import genai

load_dotenv()  # loads GEMINI_API_KEY from .env into the environment

LOGS_DIR = "logs"
DIAGNOSES_DIR = "diagnoses"
MODEL_NAME = "gemini-3.6-flash"  # current GA model, fast + free-tier friendly

client = genai.Client()  # automatically reads GEMINI_API_KEY from environment

DIAGNOSIS_PROMPT = """You are a SQL Server data diagnostics assistant. A scheduled SQL query failed. \
Given the error details below, identify the most likely root cause and suggest a concrete next step.

Respond ONLY with valid JSON in exactly this shape, with no extra text, no markdown fences:
{{
  "likely_cause": "short plain-English explanation of what went wrong",
  "affected_area": "the table/column/data pattern most likely responsible",
  "confidence": "high, medium, or low",
  "suggested_fix": "a concrete next step, e.g. a WHERE clause to isolate bad rows, or a schema check"
}}

Failure details:
Query name: {query_name}
Error type: {error_type}
Error message: {error_message}
SQL that failed:
{sql_text}
"""


def find_undiagnosed_failures():
    """Finds failure_*.json files in logs/ that don't already have a matching diagnosis."""
    os.makedirs(DIAGNOSES_DIR, exist_ok=True)
    failure_files = glob.glob(f"{LOGS_DIR}/failure_*.json")

    undiagnosed = []
    for filepath in failure_files:
        base_name = os.path.basename(filepath).replace("failure_", "diagnosis_")
        diagnosis_path = f"{DIAGNOSES_DIR}/{base_name}"
        if not os.path.exists(diagnosis_path):
            undiagnosed.append(filepath)
    return undiagnosed


def diagnose_failure(failure_path):
    with open(failure_path, "r") as f:
        failure = json.load(f)

    prompt = DIAGNOSIS_PROMPT.format(
        query_name=failure.get("query_name", "unknown"),
        error_type=failure.get("error_type", "unknown"),
        error_message=failure.get("error_message", "unknown"),
        sql_text=failure.get("sql_text", "unknown"),
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    raw_text = response.text.strip()

    # Defensive parsing in case the model wraps the JSON in markdown fences anyway
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()

    try:
        diagnosis = json.loads(raw_text)
    except json.JSONDecodeError:
        diagnosis = {
            "likely_cause": "Could not parse AI response as JSON",
            "affected_area": "unknown",
            "confidence": "low",
            "suggested_fix": "Check the raw_response field below manually",
            "raw_response": raw_text,
        }

    diagnosis["query_name"] = failure.get("query_name", "unknown")
    diagnosis["diagnosed_at"] = datetime.now().isoformat()
    diagnosis["original_error"] = failure.get("error_message", "unknown")

    return diagnosis


def main():
    undiagnosed = find_undiagnosed_failures()

    if not undiagnosed:
        print("No new failures to diagnose. All caught up.")
        return

    print(f"Found {len(undiagnosed)} failure(s) to diagnose.\n")

    for failure_path in undiagnosed:
        print(f"Diagnosing: {failure_path}")
        diagnosis = diagnose_failure(failure_path)

        base_name = os.path.basename(failure_path).replace("failure_", "diagnosis_")
        output_path = f"{DIAGNOSES_DIR}/{base_name}"
        with open(output_path, "w") as f:
            json.dump(diagnosis, f, indent=2)

        print(f"  Likely cause: {diagnosis.get('likely_cause')}")
        print(f"  Confidence:   {diagnosis.get('confidence')}")
        print(f"  Saved to:     {output_path}\n")


if __name__ == "__main__":
    main()