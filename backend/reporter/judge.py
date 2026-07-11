import os
import time
import logging

from agents import Agent, Runner
from pydantic import BaseModel, Field
from agents.extensions.models.litellm_model import LitellmModel

logger = logging.getLogger(__name__)

# Model configuration - read from env, same pattern as other agents
JUDGE_MODEL_ID = os.getenv("MODEL_ID_JUDGE", "openai/gpt-5.4-nano")


class Evaluation(BaseModel):
    feedback: str = Field(
        description="Your feedback on the financial report and rationale for your score"
    )
    score: float = Field(
        description="Score from 0 to 100 where 0 represents a terrible quality financial report and 100 represents an outstanding financial report"
    )


async def evaluate(original_instructions, original_task, original_output) -> Evaluation:
    """Evaluate the quality of a financial report using the judge model."""
    t_start = time.monotonic()

    model = LitellmModel(model=JUDGE_MODEL_ID)
    logger.info(f"Judge: START | model={JUDGE_MODEL_ID}")

    instructions = """
You are an Evaluation Agent that evaluates the quality of a financial report from a financial planning agent.
You will be provided with the instructions that were sent to the analyst, and its output, and you must evaluate the quality of the output.
"""

    task = f"""
The financial planning agent was given the following instructions:

{original_instructions}

And it was assigned this task:

{original_task}

The financial planning agent's output was:

{original_output}

Evaluate this output and respond with your comments and score.
"""

    try:
        agent = Agent(
            name="Judge Agent", instructions=instructions, model=model, output_type=Evaluation
        )
        result = await Runner.run(agent, input=task, max_turns=5)
        evaluation = result.final_output_as(Evaluation)

        t_elapsed = time.monotonic() - t_start
        logger.info(
            f"Judge: COMPLETED | model={JUDGE_MODEL_ID} | "
            f"score={evaluation.score:.1f} | time={t_elapsed:.2f}s | "
            f"feedback={evaluation.feedback[:200]}"
        )
        return evaluation

    except Exception as e:
        t_elapsed = time.monotonic() - t_start
        logger.error(
            f"Judge: FAILED | model={JUDGE_MODEL_ID} | time={t_elapsed:.2f}s | error={e}"
        )
        return Evaluation(feedback=f"Error evaluating financial report: {e}", score=80)
