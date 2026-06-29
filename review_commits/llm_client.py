"""LLM Client module for commit-reviewer.

Sends commit messages to OpenRouter API to evaluate quality.
"""

import os
import re
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-120b:free"

def review_commit(message: str) -> dict:
    """Sends a single commit message to OpenRouter and returns a structured result.

    Args:
        message: The git commit message content.

    Returns:
        A dictionary with "rating" and "reason" keys.
    """
    if not API_KEY:
        return {
            "rating": "error",
            "reason": "OPENROUTER_API_KEY is not set in .env"
        }

    prompt = (
        "You are a code review assistant evaluating git commit message quality.\n\n"
        'Rate the following commit message as exactly one of: "excellent", "good", or "bad".\n'
        "Then provide a single sentence explaining your reasoning.\n\n"
        f'Commit message: "{message}"\n\n'
        "Respond ONLY in this exact JSON format with no markdown, no code fences, nothing else:\n"
        '{"rating": "good", "reason": "Your one sentence here."}'
    )

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    except requests.exceptions.ConnectionError:
        return {
            "rating": "error",
            "reason": "Network error — could not reach OpenRouter API"
        }
    except requests.exceptions.Timeout:
        return {
            "rating": "error",
            "reason": "Request timed out after 30s"
        }
    except Exception as e:
        return {
            "rating": "error",
            "reason": f"Unexpected error: {str(e)}"
        }

    if response.status_code != 200:
        return {
            "rating": "error",
            "reason": f"API returned status {response.status_code}"
        }

    try:
        data = response.json()
    except Exception:
        return {
            "rating": "error",
            "reason": "Could not parse model response as JSON"
        }

    try:
        raw_content = data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        return {
            "rating": "error",
            "reason": "Unexpected API response shape."
        }

    # Clean markdown code fences if present
    cleaned_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
    cleaned_content = re.sub(r"\s*```$", "", cleaned_content).strip()

    try:
        result = json.loads(cleaned_content)
    except Exception:
        return {
            "rating": "error",
            "reason": "Could not parse model response as JSON"
        }

    rating = result.get("rating", "").strip().lower()
    reason = result.get("reason", "").strip()

    if rating not in ("excellent", "good", "bad"):
        rating = "error"

    return {
        "rating": rating,
        "reason": reason
    }
