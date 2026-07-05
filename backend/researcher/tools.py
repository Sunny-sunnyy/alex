# File này định nghĩa tool mà agent dùng để lưu kết quả research vào knowledge base.
# Đây là cầu nối giữa Researcher service và ingest API của Part 3.
"""
Tools for the Alex Researcher agent
"""
import logging
import os
from contextvars import ContextVar
from typing import Dict, Any
from datetime import datetime, UTC
import httpx
from agents import function_tool
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Configuration from environment
# Hai biến này là đầu nối trực tiếp sang ingest API của Part 3.
# Nếu thiếu một trong hai thì tool sẽ tự báo local mode thay vì cố gọi API lỗi.
ALEX_API_ENDPOINT = os.getenv("ALEX_API_ENDPOINT")
ALEX_API_KEY = os.getenv("ALEX_API_KEY")
_INGEST_RUN_ID: ContextVar[str | None] = ContextVar("researcher_ingest_run_id", default=None)
_LAST_INGEST_RESULT: ContextVar[Dict[str, Any] | None] = ContextVar(
    "researcher_last_ingest_result",
    default=None,
)


def set_ingest_run_id(run_id: str | None) -> None:
    """Attach the current researcher run_id to ingest telemetry."""
    _INGEST_RUN_ID.set(run_id)


def reset_ingest_observation() -> None:
    """Clear the last observed ingest result for a new researcher request."""
    _LAST_INGEST_RESULT.set(None)


def get_last_ingest_observation() -> Dict[str, Any] | None:
    """Return the last ingest result captured during the current request."""
    return _LAST_INGEST_RESULT.get()


# Hàm nội bộ này thực hiện HTTP POST thật tới ingest API.
# Nó được tách riêng để lớp retry ở bên ngoài có thể tái sử dụng mà không lặp code.
def _ingest(document: Dict[str, Any]) -> Dict[str, Any]:
    """Internal function to make the actual API call."""
    with httpx.Client() as client:
        response = client.post(
            ALEX_API_ENDPOINT,
            json=document,
            headers={"x-api-key": ALEX_API_KEY},
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
# Hàm này bọc _ingest bằng retry/backoff để chịu được cold start hoặc lỗi mạng ngắn hạn.
# Đây là lớp tăng độ bền cho tool ingest trong runtime production.
def ingest_with_retries(document: Dict[str, Any]) -> Dict[str, Any]:
    """Ingest with retry logic for SageMaker cold starts."""
    return _ingest(document)


# Đây là function tool mà agent có thể gọi trực tiếp.
# Nhiệm vụ của nó là đóng gói topic/analysis thành document và gửi sang ingest pipeline.
@function_tool
def ingest_financial_document(topic: str, analysis: str) -> Dict[str, Any]:
    """
    Ingest a financial document into the Alex knowledge base.
    
    Args:
        topic: The topic or subject of the analysis (e.g., "AAPL Stock Analysis", "Retirement Planning Guide")
        analysis: Detailed analysis or advice with specific data and insights
    
    Returns:
        Dictionary with success status and document ID
    """
    run_id = _INGEST_RUN_ID.get()
    if not ALEX_API_ENDPOINT or not ALEX_API_KEY:
        result = {
            "success": False,
            "error": "Alex API not configured. Running in local mode."
        }
        _LAST_INGEST_RESULT.set(result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s error=%s",
            run_id,
            result["success"],
            topic,
            None,
            result["error"],
        )
        return result
    
    document = {
        "text": analysis,
        "metadata": {
            "topic": topic,
            "timestamp": datetime.now(UTC).isoformat()
        }
    }
    
    try:
        ingest_result = ingest_with_retries(document)
        result = {
            "success": True,
            "document_id": ingest_result.get("document_id"),  # Changed from documentId
            "message": f"Successfully ingested analysis for {topic}"
        }
        _LAST_INGEST_RESULT.set(result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s error=%s",
            run_id,
            result["success"],
            topic,
            result["document_id"],
            None,
        )
        return result
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        _LAST_INGEST_RESULT.set(result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s error=%s",
            run_id,
            result["success"],
            topic,
            None,
            result["error"],
        )
        return result
