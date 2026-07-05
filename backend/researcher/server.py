# File này là entrypoint HTTP chính của Researcher service.
# Nhiệm vụ của nó là nhận request từ FastAPI, chạy agent nghiên cứu,
# xử lý fallback khi browser/MCP không ổn định, và trả response cho client.
"""
Alex Researcher Service - Investment Advice Agent
"""

import os
import logging
from datetime import datetime, UTC
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Agent, RunHooks, Runner, trace
from agents.exceptions import MaxTurnsExceeded
from agents.extensions.models.litellm_model import LitellmModel

# Suppress LiteLLM warnings about optional dependencies
logging.basicConfig(level=logging.INFO)
logging.getLogger("LiteLLM").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

# Import from our modules
from context import get_agent_instructions, DEFAULT_RESEARCH_PROMPT
from mcp_servers import create_playwright_mcp_server
from tools import ingest_financial_document

# Load environment
load_dotenv(override=True)

app = FastAPI(title="Alex Researcher Service")


MCP_LOGGING_ENABLED = os.getenv("MCP_LOGGING") == "True"


# Hàm nhỏ này dùng để cắt ngắn chuỗi log quá dài.
# Mục đích là giữ CloudWatch dễ đọc hơn khi tool hoặc output trả về quá nhiều dữ liệu.
def _trim_for_log(value: Any, max_length: int = 1500) -> str:
    text = str(value)
    if len(text) <= max_length:
        return text
    return f"{text[:max_length]}... [trimmed {len(text) - max_length} chars]"


# Hooks này chỉ phục vụ logging vòng đời tool khi bật MCP logging.
# Nó giúp nhìn rõ tool nào bắt đầu, kết thúc, và trả về gì trong lúc debug.
class ResearchLoggingHooks(RunHooks):
    async def on_tool_start(self, context, agent, tool) -> None:
        if MCP_LOGGING_ENABLED:
            logger.info(
                "[tool:start] name=%s type=%s repr=%s",
                getattr(tool, "name", type(tool).__name__),
                type(tool).__name__,
                _trim_for_log(repr(tool), max_length=500),
            )

    async def on_tool_end(self, context, agent, tool, result) -> None:
        if MCP_LOGGING_ENABLED:
            logger.info(
                "[tool:end] name=%s result=%s",
                getattr(tool, "name", type(tool).__name__),
                _trim_for_log(result),
            )


# Request model
class ResearchRequest(BaseModel):
    topic: Optional[str] = None  # Optional - if not provided, agent picks a topic


# Hàm này trả về model researcher đang dùng theo biến môi trường.
# Việc gom logic vào một chỗ giúp runtime chính và /health luôn báo cùng một model.
def _get_researcher_model_name() -> str:
    return os.environ.get("RESEARCHER_MODEL", "openai/gpt-5.4-nano")


# Hàm này dựng prompt đầu vào cho agent theo từng chế độ chạy.
# Nó hỗ trợ 3 trường hợp: có topic cụ thể, fallback constrained, hoặc prompt mặc định.
def _build_research_query(topic: Optional[str], constrained: bool = False) -> str:
    if topic:
        return f"Research this investment topic: {topic}"

    if constrained:
        return (
            "Research one current large-cap US investment topic. Pick only one of these names: "
            "NVDA, MSFT, AMZN, AAPL, or TSLA. Use Reuters first, or a direct MarketWatch article "
            "if Reuters is not immediately useful. Do not use finance homepages, ad links, or "
            "tracker pages. Use one content page, one snapshot, then write 3-5 concise bullets, "
            "one recommendation, and call ingest_financial_document immediately."
        )

    return DEFAULT_RESEARCH_PROMPT


# Hàm này tạo prompt fallback không dùng browser.
# Mục tiêu là vẫn tạo được một ghi chú ngắn và ingest vào knowledge base khi MCP/browser thất bại.
def _build_browserless_fallback_query(topic: Optional[str]) -> str:
    if topic:
        return (
            f"Create a short investment note about {topic} using your general market knowledge. "
            "Do not browse the web. Be explicit that this is a quick high-level note, keep it to "
            "3-5 bullets plus one recommendation, then call ingest_financial_document immediately."
        )

    return (
        "Create a short investment note about exactly one of these names: NVDA, MSFT, AMZN, AAPL, "
        "or TSLA using your general market knowledge. Do not browse the web. Be explicit that this "
        "is a quick high-level note, keep it to 3-5 bullets plus one recommendation, then call "
        "ingest_financial_document immediately."
    )


# Hàm này là lớp thực thi agent dùng chung cho cả browser mode và browserless mode.
# Nó chịu trách nhiệm tạo agent, gắn tools/MCP phù hợp, rồi gọi Runner.run().
async def _run_research_query(
    query: str,
    model: LitellmModel,
    *,
    max_turns: int,
    use_browser: bool,
) -> str:
    # Luồng xử lý:
    # 1. Mở trace để quan sát run.
    # 2. Nếu use_browser=True thì tạo Playwright MCP server.
    # 3. Tạo Agent với tools bắt buộc và MCP nếu có.
    # 4. Chạy Runner.run() với max_turns giới hạn.
    # 5. Trả final_output cho caller.
    with trace("Researcher"):
        if use_browser:
            async with create_playwright_mcp_server(timeout_seconds=120) as playwright_mcp:
                if MCP_LOGGING_ENABLED:
                    logger.info("Playwright MCP server context created")
                agent = Agent(
                    name="Alex Investment Researcher",
                    instructions=get_agent_instructions(),
                    model=model,
                    tools=[ingest_financial_document],
                    mcp_servers=[playwright_mcp],
                )

                try:
                    result = await Runner.run(
                        agent,
                        input=query,
                        max_turns=max_turns,
                        hooks=ResearchLoggingHooks() if MCP_LOGGING_ENABLED else None,
                    )
                except Exception:
                    if MCP_LOGGING_ENABLED:
                        logger.exception("Research agent run failed")
                    raise
        else:
            agent = Agent(
                name="Alex Investment Researcher",
                instructions=get_agent_instructions(),
                model=model,
                tools=[ingest_financial_document],
            )

            try:
                result = await Runner.run(
                    agent,
                    input=query,
                    max_turns=max_turns,
                    hooks=ResearchLoggingHooks() if MCP_LOGGING_ENABLED else None,
                )
            except Exception:
                if MCP_LOGGING_ENABLED:
                    logger.exception("Research agent run failed")
                raise

        if MCP_LOGGING_ENABLED:
            logger.info(
                "Research agent run completed output_preview=%s",
                _trim_for_log(result.final_output, max_length=1000),
            )

    return result.final_output


# Đây là hàm orchestration chính cho researcher.
# Nó chuẩn bị region/model, chạy browser mode trước, rồi fallback dần nếu gặp MaxTurnsExceeded.
async def run_research_agent(topic: str = None) -> str:
    """Run the research agent to generate investment advice."""

    query = _build_research_query(topic)

    if MCP_LOGGING_ENABLED:
        logger.info(
            "Starting research agent topic_provided=%s query_preview=%s",
            bool(topic),
            _trim_for_log(query, max_length=500),
        )

    region = os.environ.get("BEDROCK_REGION", "ap-southeast-1")
    os.environ["AWS_REGION_NAME"] = region
    os.environ["AWS_REGION"] = region
    os.environ["AWS_DEFAULT_REGION"] = region
    model_name = _get_researcher_model_name()
    #model = LitellmModel(model=model_name)
    #model_name = "openrouter/openai/gpt-oss-120b"
    model = LitellmModel(model=model_name)

    if MCP_LOGGING_ENABLED:
        logger.info(
            "Research agent runtime model=%s aws_region=%s aws_default_region=%s aws_region_name=%s playwright_logging=%s",
            model_name,
            os.environ.get("AWS_REGION"),
            os.environ.get("AWS_DEFAULT_REGION"),
            os.environ.get("AWS_REGION_NAME"),
            os.environ.get("DEBUG"),
        )

    # Thứ tự fallback:
    # 1. Prompt bình thường + browser.
    # 2. Prompt constrained + browser.
    # 3. Prompt browserless để tránh fail toàn request.
    try:
        return await _run_research_query(query, model, max_turns=15, use_browser=True)
    except MaxTurnsExceeded:
        fallback_query = _build_research_query(topic=topic, constrained=True)
        logger.warning(
            "Default research prompt exceeded max turns; retrying with constrained fallback query."
        )
        try:
            return await _run_research_query(
                fallback_query,
                model,
                max_turns=12,
                use_browser=True,
            )
        except MaxTurnsExceeded:
            logger.warning(
                "Browser-based fallback also exceeded max turns; retrying without browser access."
            )
            browserless_query = _build_browserless_fallback_query(topic)
            return await _run_research_query(
                browserless_query,
                model,
                max_turns=6,
                use_browser=False,
            )


# Endpoint gốc chỉ dùng như health check tối giản.
# Nó phù hợp cho kiểm tra service còn sống mà không kéo theo logic nặng.
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Alex Researcher",
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }


# Endpoint chính để sinh research theo topic hoặc để agent tự chọn topic.
# Đây là đường dẫn được test bởi test_research.py và cũng là chỗ dễ phát sinh lỗi nghiệp vụ nhất.
@app.post("/research")
async def research(request: ResearchRequest) -> str:
    """
    Generate investment research and advice.

    The agent will:
    1. Browse current financial websites for data
    2. Analyze the information found
    3. Store the analysis in the knowledge base

    If no topic is provided, the agent will pick a trending topic.
    """
    logger.info(f"MCP_LOGGING_ENABLED={MCP_LOGGING_ENABLED}")

    try:
        response = await run_research_agent(request.topic)
        return response
    except Exception as e:
        print(f"Error in research endpoint: {e}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint này dành cho scheduler chạy tự động.
# Nó luôn để agent tự chọn chủ đề thay vì nhận topic từ người dùng.
@app.get("/research/auto")
async def research_auto():
    """
    Automated research endpoint for scheduled runs.
    Picks a trending topic automatically and generates research.
    Used by EventBridge Scheduler for periodic research updates.
    """
    try:
        # Always use agent's choice for automated runs
        response = await run_research_agent(topic=None)
        return {
            "status": "success",
            "timestamp": datetime.now(UTC).isoformat(),
            "message": "Automated research completed",
            "preview": response[:200] + "..." if len(response) > 200 else response,
        }
    except Exception as e:
        print(f"Error in automated research: {e}")
        return {"status": "error", "timestamp": datetime.now(UTC).isoformat(), "error": str(e)}


# Endpoint này trả health chi tiết hơn root endpoint.
# Nó hữu ích để xác nhận model hiện tại, region, và trạng thái cấu hình ingest/MCP.
@app.get("/health")
async def health():
    """Detailed health check."""
    # Debug container detection
    container_indicators = {
        "dockerenv": os.path.exists("/.dockerenv"),
        "containerenv": os.path.exists("/run/.containerenv"),
        "aws_execution_env": os.environ.get("AWS_EXECUTION_ENV", ""),
        "ecs_container_metadata": os.environ.get("ECS_CONTAINER_METADATA_URI", ""),
        "kubernetes_service": os.environ.get("KUBERNETES_SERVICE_HOST", ""),
    }

    return {
        "service": "Alex Researcher",
        "status": "healthy",
        "alex_api_configured": bool(os.getenv("ALEX_API_ENDPOINT") and os.getenv("ALEX_API_KEY")),
        "timestamp": datetime.now(UTC).isoformat(),
        "debug_container": container_indicators,
        "aws_region": os.environ.get("AWS_DEFAULT_REGION", "not set"),
        "researcher_model": _get_researcher_model_name(),
        "mcp_logging_enabled": MCP_LOGGING_ENABLED,
    }


# Endpoint phụ này dùng để thử kết nối Bedrock trực tiếp khi cần debug môi trường cũ.
# Dù runtime hiện tại có thể dùng OpenAI model, endpoint này vẫn hữu ích cho kiểm tra hạ tầng AWS.
@app.get("/test-bedrock")
async def test_bedrock():
    """Test Bedrock connection directly."""
    try:
        import boto3

        region = os.environ.get("BEDROCK_REGION", "us-west-2")
        model_id = os.environ.get("RESEARCHER_MODEL", "bedrock/global.openai.gpt-oss-120b-1:0")

        os.environ["AWS_REGION_NAME"] = region
        os.environ["AWS_REGION"] = region
        os.environ["AWS_DEFAULT_REGION"] = region

        session = boto3.Session()
        actual_region = session.region_name

        client = boto3.client("bedrock-runtime", region_name=region)

        try:
            bedrock_client = boto3.client("bedrock", region_name=region)
            models = bedrock_client.list_foundation_models()
            openai_models = [
                m["modelId"] for m in models["modelSummaries"] if "openai" in m["modelId"].lower()
            ]
        except Exception as list_error:
            openai_models = f"Error listing: {str(list_error)}"

        model = LitellmModel(model=model_id)

        agent = Agent(
            name="Test Agent",
            instructions="You are a helpful assistant. Be very brief.",
            model=model,
        )

        result = await Runner.run(agent, input="Say hello in 5 words or less", max_turns=1)

        return {
            "status": "success",
            "model": str(model.model),  # Use actual model from LitellmModel
            "region": actual_region,
            "response": result.final_output,
            "debug": {
                "boto3_session_region": actual_region,
                "available_openai_models": openai_models,
            },
        }
    except Exception as e:
        import traceback

        return {
            "status": "error",
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "debug": {
                "boto3_session_region": session.region_name if "session" in locals() else "unknown",
                "env_vars": {
                    "AWS_REGION_NAME": os.environ.get("AWS_REGION_NAME"),
                    "AWS_REGION": os.environ.get("AWS_REGION"),
                    "AWS_DEFAULT_REGION": os.environ.get("AWS_DEFAULT_REGION"),
                },
            },
        }


# Khối này cho phép chạy FastAPI trực tiếp ở local bằng uvicorn.
# Nó không dùng trong Lambda production, nhưng tiện cho local development.
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
