"""
Shared guardrail utilities for Alex agents.
Guide 8 Section 4: input validation, output verification, response size limits.
"""

import json
import logging

logger = logging.getLogger(__name__)

# Prompt injection detection patterns (case-insensitive match)
_DANGEROUS_PATTERNS = [
    "ignore previous instructions",
    "disregard all prior",
    "forget everything",
    "new instructions:",
    "system:",
    "assistant:",
]


def validate_chart_data(chart_json: str) -> tuple[bool, str, dict]:
    """
    Validate that charter agent output is well-formed JSON with expected structure.

    Args:
        chart_json: Raw JSON string from the Charter agent.

    Returns:
        (is_valid, error_message, parsed_data).
        On failure, is_valid=False and parsed_data is {}.
    """
    try:
        data = json.loads(chart_json)

        if "charts" not in data:
            return False, "Missing required key: 'charts'", {}

        if not isinstance(data["charts"], list):
            return False, "Key 'charts' must be an array", {}

        for i, chart in enumerate(data["charts"]):
            if "type" not in chart:
                return False, f"Chart {i} missing 'type' field", {}
            if "data" not in chart:
                return False, f"Chart {i} missing 'data' field", {}
            if not isinstance(chart["data"], list):
                return False, f"Chart {i} data must be an array", {}

            if chart["type"] == "pie":
                for point in chart["data"]:
                    if "name" not in point or "value" not in point:
                        return False, f"Pie chart data points must have 'name' and 'value'", {}
            elif chart["type"] == "bar":
                for point in chart["data"]:
                    if "category" not in point:
                        return False, f"Bar chart data points must have 'category'", {}

        return True, "", data

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from charter agent: {e}")
        return False, f"Invalid JSON: {e}", {}
    except Exception as e:
        logger.error(f"Unexpected error validating chart data: {e}")
        return False, f"Validation error: {e}", {}


def sanitize_user_input(text: str) -> str:
    """
    Check for prompt injection attempts in user-provided text.

    Returns "[INVALID INPUT DETECTED]" if injection patterns found,
    otherwise returns the original text unchanged.
    """
    if not text:
        return text

    text_lower = text.lower()
    for pattern in _DANGEROUS_PATTERNS:
        if pattern in text_lower:
            logger.warning(f"Potential prompt injection detected: pattern='{pattern}'")
            return "[INVALID INPUT DETECTED]"

    return text


def truncate_response(text: str, max_length: int = 50000) -> str:
    """
    Ensure response does not exceed reasonable size.

    Returns truncated text with a warning marker if truncation occurred.
    """
    if len(text) > max_length:
        logger.warning(f"Response truncated from {len(text)} to {max_length} characters")
        return text[:max_length] + "\n\n[Response truncated due to length]"
    return text
