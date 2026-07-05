#!/usr/bin/env python3
# File này là script test end-to-end cho Researcher service đã deploy.
# Nó tự tìm researcher URL, kiểm tra health, rồi gọi /research để quan sát kết quả thực tế.
"""
Test the researcher service by generating investment research.
Cross-platform script for Mac/Windows/Linux.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests


TERRAFORM_DIR = "terraform/4_researcher"


# Hàm này là classifier "nhẹ" ở phía client terminal.
# Nó không nhìn vào CloudWatch, chỉ suy luận từ response text để báo nhanh run này verified hay fallback.
def classify_terminal_result(result_text: str) -> tuple[str, str | None]:
    """Classify the terminal-visible result without changing the API contract."""
    lowered = result_text.lower()

    fallback_markers = [
        "quick high-level note",
        "quick high-level fallback note",
        "no web research",
        "web research failed",
        "web research blocked",
        "web sources blocked",
        "non-web-browsed overview",
        "fallback note",
        "general market knowledge",
        "could not verify",
        "failed to access a clean direct article page",
        "no clean direct article found",
        "direct article pages were not accessible",
        "direct article pages are blocked or unusable",
        "couldn’t access clean direct articles",
        "couldn't access clean direct articles",
        "page not found (404)",
        "page not found",
        "page unavailable",
        "404 / unavailable",
        "404 (“page not found”)",
        '404 ("page not found")',
        "just a moment",
        "access restricted",
        "access temporarily restricted",
        "access-restricted",
        "browsing blocked",
        "clean, accessible article content",
        "usable direct article page",
        "non-article/portal layouts",
        "unable to verify clean direct article pages",
        "couldn’t reliably quote",
        "couldn't reliably quote",
        "couldn’t base the analysis on a usable direct article page",
        "couldn't base the analysis on a usable direct article page",
        "did not provide clean, accessible article content",
        "did not obtain a usable accessible article body",
        "i can’t responsibly extract verified",
        "i can't responsibly extract verified",
        "could not responsibly state",
        "i tried to pull a direct article page",
        "error page",
        "error”",
        'error"',
    ]

    for marker in fallback_markers:
        if marker in lowered:
            return "success_fallback", marker

    return "success_verified", None


# Hàm này xác định repo root bằng git để script chạy ổn từ nhiều thư mục khác nhau.
def get_repo_root() -> Path:
    return Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    )


# Hàm này lấy URL public của researcher service.
# Nó hỗ trợ cả local mode và mode lấy output từ Terraform.
def get_service_url():
    """Get the researcher service URL."""
    if os.getenv("LOCAL") == "True":
        return "http://localhost:8000"

    try:
        result = subprocess.run(
            ["terraform", "output", "-raw", "researcher_url"],
            capture_output=True,
            text=True,
            check=True,
            cwd=get_repo_root() / TERRAFORM_DIR,
        )
        return result.stdout.strip().rstrip("/")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error getting researcher URL: {e}")
        print("   Make sure terraform/4_researcher has been applied after deploying the image.")
        sys.exit(1)


# Đây là luồng test chính của script.
# Nó lần lượt kiểm tra URL, gọi /health, rồi gọi /research và in kết quả ra console.
def test_research(topic=None):
    """Test the researcher service with a topic."""
    # If no topic, let the agent pick one
    display_topic = topic if topic else "Agent's choice (trending topic)"

    # Get service URL
    print("Getting researcher service URL...")
    service_url = get_service_url()

    if not service_url:
        print("❌ Could not get service URL")
        sys.exit(1)

    print(f"✅ Found service at: {service_url}")

    # Test health endpoint first
    print("\nChecking service health...")
    try:
        health_url = f"{service_url}/health"
        response = requests.get(health_url, timeout=10)
        response.raise_for_status()
        health_payload = response.json()
        active_model = health_payload.get("researcher_model", "unknown")
        print("✅ Service is healthy")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        print("   The service may still be starting. Try again in a minute.")
        sys.exit(1)

    # Call research endpoint
    print(f"\n🔬 Generating research for: {display_topic}")
    print("   This will take 20-30 seconds as the agent researches and analyzes...")

    try:
        research_url = f"{service_url}/research"
        # Only include topic in payload if it's provided
        payload = {"topic": topic} if topic else {}
        request_started = time.perf_counter()
        response = requests.post(
            research_url,
            json=payload,
            timeout=180  # Give it 3 minutes for research
        )
        request_duration_ms = int((time.perf_counter() - request_started) * 1000)
        response.raise_for_status()

        # Parse and display the result
        result = response.json()
        outcome, degraded_signal = classify_terminal_result(result)
        ingest_status = "assumed_success"

        print("\n✅ Research generated successfully!")
        print("\nRUN SUMMARY")
        print("=" * 60)
        print(f"Model: {active_model}")
        print(f"Topic: {display_topic}")
        print(f"Request Duration (ms): {request_duration_ms}")
        print(f"Outcome: {outcome}")
        print(f"Degraded Signal: {degraded_signal or 'none'}")
        print(f"Ingest Status: {ingest_status}")
        print("=" * 60)
        print("\n" + "=" * 60)
        print("RESEARCH RESULT:")
        print("=" * 60)
        print(result)
        print("=" * 60)

        print("\n✅ The research has been automatically stored in your knowledge base.")
        print("   To verify, run:")
        print("     cd ../ingest")
        print("     uv run test_search_s3vectors.py")

    except requests.exceptions.Timeout:
        print("❌ Request timed out. The service might be under heavy load.")
        print("   Try again in a moment.")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling research endpoint: {e}")
        if hasattr(e, "response") and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Error details: {error_detail}")
            except (json.JSONDecodeError, AttributeError):
                print(f"   Response: {e.response.text}")
        sys.exit(1)


# Hàm main chỉ lo parse CLI arguments rồi gọi test_research().
# Cách tách này giúp script dễ đọc và dễ mở rộng về sau.
def main():
    parser = argparse.ArgumentParser(
        description="Test the Alex Researcher service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Let agent pick a trending topic
  uv run test_research.py

  # Research specific topic
  uv run test_research.py "Tesla competitive advantages"

  # Research another topic
  uv run test_research.py "Microsoft cloud revenue growth"
        """,
    )
    parser.add_argument(
        "topic",
        nargs="?",
        default=None,
        help="Investment topic to research (optional - agent will pick trending topic if not provided)",
    )

    args = parser.parse_args()
    test_research(args.topic)


if __name__ == "__main__":
    main()
