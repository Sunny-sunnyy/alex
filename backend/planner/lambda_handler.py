"""
Financial Planner Orchestrator Lambda Handler
Uses OpenAI model via LiteLLM.
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, Any

from agents import Agent, Runner, trace
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from litellm.exceptions import RateLimitError

try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
except ImportError:
    pass

# Import database package
from src import Database

from templates import ORCHESTRATOR_INSTRUCTIONS
from agent import create_agent, handle_missing_instruments, load_portfolio_summary, MODEL_ID
from market import update_instrument_prices
from observability import observe

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize database
db = Database()

@retry(
    retry=retry_if_exception_type(RateLimitError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    before_sleep=lambda retry_state: logger.info(f"Planner: Rate limit hit, retrying in {retry_state.next_action.sleep} seconds...")
)
async def run_orchestrator(job_id: str) -> None:
    """Run the orchestrator agent to coordinate portfolio analysis."""
    t_start = time.monotonic()
    logger.info(f"run_orchestrator START | job={job_id} | model={MODEL_ID}")
    try:
        # Update job status to running
        db.jobs.update_status(job_id, 'running')

        # Handle missing instruments first (non-agent pre-processing)
        t_pre_start = time.monotonic()
        await asyncio.to_thread(handle_missing_instruments, job_id, db)

        # Update instrument prices after tagging
        logger.info("Planner: Updating instrument prices from market data")
        await asyncio.to_thread(update_instrument_prices, job_id, db)
        t_pre = time.monotonic() - t_pre_start
        logger.info(f"[TIMING] Pre-processing phase: {t_pre:.2f}s")

        # Load portfolio summary (just statistics, not full data)
        portfolio_summary = await asyncio.to_thread(load_portfolio_summary, job_id, db)

        # Create agent with tools and context
        model, tools, task, context, effective_model = create_agent(job_id, portfolio_summary, db)

        # Run the orchestrator
        t_agent_start = time.monotonic()
        with trace("Planner Orchestrator"):
            from agent import PlannerContext
            agent = Agent[PlannerContext](
                name="Financial Planner",
                instructions=ORCHESTRATOR_INSTRUCTIONS,
                model=model,
                tools=tools
            )

            result = await Runner.run(
                agent,
                input=task,
                context=context,
                max_turns=20
            )

            # Mark job as completed after all agents finish
            db.jobs.update_status(job_id, "completed")

        t_agent = time.monotonic() - t_agent_start
        t_total = time.monotonic() - t_start
        logger.info(f"[TIMING] Agent orchestration phase: {t_agent:.2f}s | model={effective_model}")
        logger.info(
            f"[TIMING] run_orchestrator TOTAL: {t_total:.2f}s "
            f"(pre={t_pre:.2f}s, agent={t_agent:.2f}s) | model={effective_model}"
        )
        logger.info(f"Planner: Job {job_id} completed successfully")

    except Exception as e:
        t_total = time.monotonic() - t_start
        logger.error(f"Planner: Error in orchestration after {t_total:.2f}s: {e}", exc_info=True)
        db.jobs.update_status(job_id, 'failed', error_message=str(e))
        raise

def lambda_handler(event, context):
    """
    Lambda handler for SQS-triggered orchestration.

    Expected event from SQS:
    {
        "Records": [
            {
                "body": "job_id"
            }
        ]
    }
    """
    t_lambda_start = time.monotonic()
    logger.info(f"lambda_handler START | model={MODEL_ID}")

    # Wrap entire handler with observability context
    with observe():
        try:
            logger.info(f"Planner Lambda invoked with event: {json.dumps(event)[:500]}")

            # Extract job_id from SQS message
            if 'Records' in event and len(event['Records']) > 0:
                # SQS message
                job_id = event['Records'][0]['body']
                if isinstance(job_id, str) and job_id.startswith('{'):
                    # Body might be JSON
                    try:
                        body = json.loads(job_id)
                        job_id = body.get('job_id', job_id)
                    except json.JSONDecodeError:
                        pass
            elif 'job_id' in event:
                # Direct invocation
                job_id = event['job_id']
            else:
                logger.error("No job_id found in event")
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No job_id provided'})
                }

            logger.info(f"Planner: Starting orchestration for job {job_id}")

            # Run the orchestrator
            asyncio.run(run_orchestrator(job_id))

            t_total = time.monotonic() - t_lambda_start
            logger.info(
                f"[TIMING] lambda_handler TOTAL: {t_total:.2f}s | "
                f"job={job_id} | model={MODEL_ID}"
            )

            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'message': f'Analysis completed for job {job_id}',
                    'model': MODEL_ID,
                    'timing': {
                        'lambda_total_s': round(t_total, 2),
                    },
                })
            }

        except Exception as e:
            t_total = time.monotonic() - t_lambda_start
            logger.error(f"Planner: Error in lambda handler after {t_total:.2f}s: {e}", exc_info=True)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'success': False,
                    'error': str(e)
                })
            }

# For local testing
if __name__ == "__main__":
    # Define a test user
    test_user_id = "test_user_planner_local"

    # Ensure the test user exists before creating a job
    from src.schemas import UserCreate, JobCreate
    
    user = db.users.find_by_clerk_id(test_user_id)
    if not user:
        print(f"Creating test user: {test_user_id}")
        user_create = UserCreate(clerk_user_id=test_user_id, display_name="Test Planner User")
        db.users.create(user_create.model_dump(), returning='clerk_user_id')

    # Create a test job
    print("Creating test job...")
    job_create = JobCreate(
        clerk_user_id=test_user_id,
        job_type='portfolio_analysis',
        request_payload={
            'analysis_type': 'comprehensive',
            'test': True
        }
    )
    
    job = db.jobs.create(job_create.model_dump())
    job_id = job
    
    print(f"Created test job: {job_id}")
    
    # Test the handler
    test_event = {
        'job_id': job_id
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))