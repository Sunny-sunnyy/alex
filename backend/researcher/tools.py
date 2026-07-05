# File này định nghĩa tool mà agent dùng để lưu kết quả research vào knowledge base.
# Đây là cầu nối giữa Researcher service và ingest API của Part 3.
"""
Tools for the Alex Researcher agent
"""
import logging
import os
from contextvars import ContextVar
from threading import Lock
from typing import Dict, Any
from datetime import datetime, UTC
from urllib.parse import urlparse
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
_INGEST_OBSERVATIONS: dict[str, Dict[str, Any]] = {}
_INGEST_OBSERVATIONS_LOCK = Lock()
_ALLOWED_SOURCE_DOMAINS = (
    "investopedia.com",
    "apnews.com",
    "cnn.com",
    "reuters.com",
)
_BLOCKED_SOURCE_MARKERS = (
    "about:blank",
    "about:srcdoc",
    "client_storage",
    "optimizely",
    "captcha",
    "consent",
    "error",
)
_DEGRADED_ANALYSIS_MARKERS = (
    "quick high-level note",
    "quick high-level fallback note",
    "general market knowledge",
    "fallback note",
    "web research failed",
    "verified web content was not obtained",
    "could not obtain verified web content",
)


def set_ingest_run_id(run_id: str | None) -> None:
    """Attach the current researcher run_id to ingest telemetry."""
    _INGEST_RUN_ID.set(run_id)


def reset_ingest_observation() -> None:
    """Clear the last observed ingest result for a new researcher request."""
    run_id = _INGEST_RUN_ID.get()
    if not run_id:
        return
    with _INGEST_OBSERVATIONS_LOCK:
        _INGEST_OBSERVATIONS.pop(run_id, None)


def get_last_ingest_observation(run_id: str | None) -> Dict[str, Any] | None:
    """Return the last ingest result captured for the given researcher run."""
    if not run_id:
        return None
    with _INGEST_OBSERVATIONS_LOCK:
        observation = _INGEST_OBSERVATIONS.get(run_id)
        return dict(observation) if observation is not None else None


def clear_ingest_observation(run_id: str | None) -> None:
    """Drop ingest observation once request-level summary has been emitted."""
    if not run_id:
        return
    with _INGEST_OBSERVATIONS_LOCK:
        _INGEST_OBSERVATIONS.pop(run_id, None)


def _record_ingest_observation(run_id: str | None, result: Dict[str, Any]) -> None:
    """Persist ingest observation in a process-wide map keyed by run_id."""
    if not run_id:
        return
    with _INGEST_OBSERVATIONS_LOCK:
        _INGEST_OBSERVATIONS[run_id] = dict(result)


def _is_allowed_source_url(source_url: str) -> bool:
    parsed = urlparse(source_url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    lowered_url = source_url.lower()
    if any(marker in lowered_url for marker in _BLOCKED_SOURCE_MARKERS):
        return False
    host = parsed.netloc.lower()
    return any(domain in host for domain in _ALLOWED_SOURCE_DOMAINS)


def _looks_like_degraded_analysis(analysis: str) -> bool:
    lowered = analysis.lower()
    return any(marker in lowered for marker in _DEGRADED_ANALYSIS_MARKERS)


def _normalize_analysis(analysis: str, source_url: str) -> str:
    cleaned = analysis.strip()
    if "source url:" in cleaned.lower():
        return cleaned
    return f"Source URL: {source_url}\n\n{cleaned}"


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
def ingest_financial_document(topic: str, analysis: str, source_url: str) -> Dict[str, Any]:
    """
    Ingest a financial document into the Alex knowledge base.
    
    Args:
        topic: The topic or subject of the analysis (e.g., "AAPL Stock Analysis", "Retirement Planning Guide")
        analysis: Detailed analysis or advice with specific data and insights
    
    Returns:
        Dictionary with success status and document ID
    """
    run_id = _INGEST_RUN_ID.get()
    if not _is_allowed_source_url(source_url):
        result = {
            "success": False,
            "error": "Verified web content required: source_url must be a clean direct article URL.",
            "source_url": source_url,
        }
        _record_ingest_observation(run_id, result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s source_url=%s error=%s",
            run_id,
            result["success"],
            topic,
            None,
            source_url,
            result["error"],
        )
        return result

    if _looks_like_degraded_analysis(analysis):
        result = {
            "success": False,
            "error": "Verified web content required: refusing to ingest degraded or fallback analysis.",
            "source_url": source_url,
        }
        _record_ingest_observation(run_id, result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s source_url=%s error=%s",
            run_id,
            result["success"],
            topic,
            None,
            source_url,
            result["error"],
        )
        return result

    if not ALEX_API_ENDPOINT or not ALEX_API_KEY:
        result = {
            "success": False,
            "error": "Alex API not configured. Running in local mode.",
            "source_url": source_url,
        }
        _record_ingest_observation(run_id, result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s source_url=%s error=%s",
            run_id,
            result["success"],
            topic,
            None,
            source_url,
            result["error"],
        )
        return result
    
    document = {
        "text": _normalize_analysis(analysis, source_url),
        "metadata": {
            "topic": topic,
            "timestamp": datetime.now(UTC).isoformat(),
            "source_url": source_url,
        }
    }
    
    try:
        ingest_result = ingest_with_retries(document)
        result = {
            "success": True,
            "document_id": ingest_result.get("document_id"),  # Changed from documentId
            "message": f"Successfully ingested analysis for {topic}",
            "source_url": source_url,
        }
        _record_ingest_observation(run_id, result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s source_url=%s error=%s",
            run_id,
            result["success"],
            topic,
            result["document_id"],
            source_url,
            None,
        )
        return result
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
            "source_url": source_url,
        }
        _record_ingest_observation(run_id, result)
        logger.info(
            "research_ingest run_id=%s success=%s topic=%s document_id=%s source_url=%s error=%s",
            run_id,
            result["success"],
            topic,
            None,
            source_url,
            result["error"],
        )
        return result
