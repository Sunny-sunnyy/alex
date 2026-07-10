"""
Audit logging for AI decisions.
Guide 8 Section 5: compliance audit trail with CloudWatch + LangFuse dual output.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """Static audit logger for AI agent decisions."""

    @staticmethod
    def log_ai_decision(
        agent_name: str,
        job_id: str,
        input_data: Dict[str, Any],
        output_data: Any,
        model_used: str,
        duration_ms: int,
        observability: Any = None,
    ) -> dict:
        """
        Record an auditable AI decision to CloudWatch and optionally LangFuse.

        Args:
            agent_name: e.g. "planner", "reporter", "charter", "retirement", "tagger"
            job_id: The analysis job UUID.
            input_data: The task/prompt data sent to the agent.
            output_data: The agent's final output (str or dict).
            model_used: The LiteLLM model string.
            duration_ms: Total agent execution time in milliseconds.
            observability: Optional observability context for LangFuse events.

        Returns:
            The audit entry dict that was logged.
        """
        output_type = type(output_data).__name__
        try:
            output_size = len(json.dumps(output_data))
        except (TypeError, ValueError):
            output_size = len(str(output_data))

        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": "AI_DECISION",
            "agent": agent_name,
            "job_id": job_id,
            "model": model_used,
            "input_hash": hashlib.sha256(
                json.dumps(input_data, sort_keys=True, default=str).encode()
            ).hexdigest(),
            "output_summary": {
                "type": output_type,
                "size_bytes": output_size,
            },
            "duration_ms": duration_ms,
        }

        # CloudWatch structured log
        logger.info(json.dumps(audit_entry))

        # LangFuse event (when observability context is available)
        if observability is not None:
            try:
                observability.create_event(
                    name="AI Decision Audit",
                    status_message=json.dumps(audit_entry),
                )
            except Exception as e:
                logger.warning(f"AuditLogger: Failed to send LangFuse event: {e}")

        return audit_entry
