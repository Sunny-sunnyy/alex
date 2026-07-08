#!/usr/bin/env python3
"""
Simple test for Retirement agent — OpenAI model.
"""

import time
import json
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate
from lambda_handler import lambda_handler
from agent import MODEL_ID

def test_retirement():
    """Test the retirement agent with simple portfolio data"""

    # Create a real job in the database
    db = Database()
    job_create = JobCreate(
        clerk_user_id="test_user_001",
        job_type="portfolio_analysis",
        request_payload={"test": True}
    )
    job_id = db.jobs.create(job_create.model_dump())
    print(f"Created test job: {job_id}")

    test_event = {
        "job_id": job_id,
        "portfolio_data": {
            "accounts": [
                {
                    "name": "401(k)",
                    "type": "retirement",
                    "cash_balance": 10000,
                    "positions": [
                        {
                            "symbol": "SPY",
                            "quantity": 100,
                            "instrument": {
                                "name": "SPDR S&P 500 ETF",
                                "current_price": 450,
                                "allocation_asset_class": {"equity": 100}
                            }
                        }
                    ]
                }
            ]
        }
    }

    print("Testing Retirement Agent...")
    print(f"Model: {MODEL_ID}")
    print("=" * 60)

    t_start = time.monotonic()
    result = lambda_handler(test_event, None)
    t_total = time.monotonic() - t_start

    print(f"Status Code: {result['statusCode']}")

    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"Success: {body.get('success', False)}")
        print(f"Message: {body.get('message', 'N/A')}")
        print(f"Model: {body.get('model', 'unknown')}")
        timing = body.get('timing', {})
        if timing:
            print(f"Timing: create={timing.get('create_s')}s, "
                  f"agent={timing.get('agent_s')}s, "
                  f"db={timing.get('db_s')}s, "
                  f"lambda_total={timing.get('lambda_total_s')}s")

        # Check what was actually saved in the database
        print("\n" + "=" * 60)
        print("CHECKING DATABASE CONTENT")
        print("=" * 60)

        job = db.jobs.find_by_id(job_id)
        if job and job.get('retirement_payload'):
            payload = job['retirement_payload']
            print(f"Retirement data found in database")
            print(f"Payload keys: {list(payload.keys())}")

            if 'analysis' in payload:
                analysis = payload['analysis']
                print(f"\nAnalysis type: {type(analysis).__name__}")

                if isinstance(analysis, str):
                    print(f"Analysis length: {len(analysis)} characters")

                    # Show first 500 characters and last 200 characters
                    print(f"\nFirst 500 characters:")
                    print("-" * 40)
                    print(analysis[:500])
                    print("-" * 40)

                    if len(analysis) > 700:
                        print(f"\nLast 200 characters:")
                        print("-" * 40)
                        print(analysis[-200:])
                        print("-" * 40)
                else:
                    print(f"Analysis is not a string: {type(analysis)}")
                    print(f"Content: {str(analysis)[:200]}")

            print(f"\nGenerated at: {payload.get('generated_at', 'N/A')}")
            print(f"Agent: {payload.get('agent', 'N/A')}")
        else:
            print("No retirement data found in database")
    else:
        print(f"Error: {result['body']}")

    # Clean up - delete the test job
    db.jobs.delete(job_id)
    print(f"\nDeleted test job: {job_id}")

    print(f"Wall-clock total: {t_total:.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    test_retirement()