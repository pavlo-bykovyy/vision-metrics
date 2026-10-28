import json
import re
from typing import Dict, Any


def format_judge_prompt(system_prompt: str, input_text: str, generated_text: str) -> str:
    """Formats the input text and generated response into a prompt for the judge LLM."""
    return (
        f"{system_prompt}\n\n"
        f"--- INPUT TEXT ---\n{input_text}\n\n"
        f"--- GENERATED RESPONSE ---\n{generated_text}\n\n"
        f"JSON EVALUATION:"
    )

def parse_judge_json(text_output: str) -> Dict[str, Any]:
    """
    Safely extracts and parses a JSON object from messy LLM output.
    Hunts for the outermost brackets to ignore conversational fluff.
    """
    try:
        clean_text = re.sub(r"```(?:json)?\n?(.*?)\n?```", r"\1", text_output.strip(), flags=re.DOTALL)

        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = clean_text[start_idx : end_idx + 1]
            return json.loads(json_str)

    except (json.JSONDecodeError, ValueError):
        pass

    return {}