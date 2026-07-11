#!/usr/bin/env python3
"""
Full test for Reporter agent via Lambda — OpenAI model.
"""

import os
import json
import time
import boto3
from dotenv import load_dotenv

load_dotenv(override=True)

from src import Database
from src.schemas import JobCreate

def test_reporter_lambda():
    """Test the Reporter agent via Lambda invocation"""

    db = Database()
    lambda_client = boto3.client('lambda')

    # Create test job
    test_user_id = "test_user_001"

    job_create = JobCreate(
        clerk_user_id=test_user_id,
        job_type="portfolio_analysis",
        request_payload={"analysis_type": "test", "test": True}
    )
    job_id = db.jobs.create(job_create.model_dump())

    print(f"Testing Reporter Lambda with job {job_id}")
    print("=" * 60)

    # Invoke Lambda
    try:
        t_start = time.monotonic()
        response = lambda_client.invoke(
            FunctionName='alex-reporter',
            InvocationType='RequestResponse',
            Payload=json.dumps({'job_id': job_id})
        )
        t_invoke = time.monotonic() - t_start

        result = json.loads(response['Payload'].read())

        # Parse body for timing/model info if available
        body = result.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)

        model_used = body.get('model', 'unknown')
        timing = body.get('timing', {})

        print(f"\nLambda invoke time: {t_invoke:.2f}s")
        print(f"Model: {model_used}")
        if timing:
            print(f"Timing: create={timing.get('create_s')}s, "
                  f"agent={timing.get('agent_s')}s, "
                  f"db={timing.get('db_s')}s, "
                  f"lambda_total={timing.get('lambda_total_s')}s")
        print(f"\nLambda Response: {json.dumps(result, indent=2)}")

        # Check database for results
        time.sleep(2)  # Give it a moment
        job = db.jobs.find_by_id(job_id)

        if job and job.get('report_payload'):
            print("\nReport generated successfully!")
            payload = job['report_payload']
            content = payload.get('content', '')
            print(f"Report length: {len(content)} characters")
            if content:
                preview = content[:500]
                if len(content) > 500:
                    preview += "..."
                print(f"Report preview: {preview}")
        else:
            print("\nNo report found in database")

    except Exception as e:
        print(f"Error invoking Lambda: {e}")

    print("=" * 60)

if __name__ == "__main__":
    test_reporter_lambda()
