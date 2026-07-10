"""
InstrumentTagger Lambda Handler
Classifies financial instruments and updates the database.
Uses OpenAI model via LiteLLM.
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from src import Database
from src.schemas import InstrumentCreate
from agent import tag_instruments, classification_to_db_format, MODEL_ID
from observability import observe
from alex_shared.audit import AuditLogger

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize database
db = Database()

async def process_instruments(instruments: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Process and classify instruments asynchronously.

    Args:
        instruments: List of instruments to classify

    Returns:
        Processing results
    """
    t_start = time.monotonic()
    logger.info(f"process_instruments: {len(instruments)} instruments | model={MODEL_ID}")

    # Guide 8: structured event logging
    logger.info(json.dumps({
        "event": "TAGGER_STARTED",
        "job_id": "batch",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL_ID,
        "instrument_count": len(instruments),
    }))

    # Run the classification
    classifications = await tag_instruments(instruments)

    t_classify = time.monotonic() - t_start
    logger.info(f"[TIMING] Classification phase: {t_classify:.2f}s")

    # Update database with classifications
    updated = []
    errors = []

    for classification in classifications:
        try:
            # Convert to database format
            db_instrument = classification_to_db_format(classification)

            # Check if instrument exists
            existing = db.instruments.find_by_symbol(classification.symbol)

            if existing:
                # Update existing instrument
                update_data = db_instrument.model_dump()
                # Remove symbol as it's the key
                del update_data['symbol']

                rows = db.client.update(
                    'instruments',
                    update_data,
                    "symbol = :symbol",
                    {'symbol': classification.symbol}
                )
                logger.info(f"Updated {classification.symbol} in database ({rows} rows)")
            else:
                # Create new instrument
                db.instruments.create_instrument(db_instrument)
                logger.info(f"Created {classification.symbol} in database")

            updated.append(classification.symbol)

        except Exception as e:
            logger.error(f"Error updating {classification.symbol}: {e}")
            errors.append({
                'symbol': classification.symbol,
                'error': str(e)
            })

    t_total = time.monotonic() - t_start
    logger.info(
        f"[TIMING] process_instruments total: {t_total:.2f}s "
        f"(classify={t_classify:.2f}s, db={t_total - t_classify:.2f}s) | model={MODEL_ID}"
    )

    # Guide 8: structured completion event
    logger.info(json.dumps({
        "event": "TAGGER_COMPLETED",
        "duration_ms": int(t_total * 1000),
        "model": MODEL_ID,
        "updated_count": len(updated),
        "error_count": len(errors),
    }))

    # Prepare response (convert Pydantic models to dicts)
    return {
        'tagged': len(classifications),
        'updated': updated,
        'errors': errors,
        'model': MODEL_ID,
        'timing': {
            'total_s': round(t_total, 2),
            'classify_s': round(t_classify, 2),
            'db_s': round(t_total - t_classify, 2),
        },
        'classifications': [
            {
                'symbol': c.symbol,
                'name': c.name,
                'type': c.instrument_type,
                'current_price': c.current_price,
                'asset_class': c.allocation_asset_class.model_dump(),
                'regions': c.allocation_regions.model_dump(),
                'sectors': c.allocation_sectors.model_dump()
            }
            for c in classifications
        ]
    }

def lambda_handler(event, context):
    """
    Lambda handler for instrument tagging.

    Expected event format:
    {
        "instruments": [
            {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF"},
            ...
        ]
    }
    """
    t_lambda_start = time.monotonic()
    logger.info(f"lambda_handler START | model={MODEL_ID}")

    # Wrap entire handler with observability context
    with observe():
        try:
            # Parse the event
            instruments = event.get('instruments', [])

            if not instruments:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'No instruments provided'})
                }

            # Process all instruments in a single async context
            result = asyncio.run(process_instruments(instruments))

            t_total = time.monotonic() - t_lambda_start
            result['timing']['lambda_total_s'] = round(t_total, 2)
            logger.info(
                f"[TIMING] lambda_handler TOTAL: {t_total:.2f}s | "
                f"instruments={len(instruments)} | model={MODEL_ID}"
            )

            return {
                'statusCode': 200,
                'body': json.dumps(result)
            }

        except Exception as e:
            t_total = time.monotonic() - t_lambda_start
            logger.error(f"Lambda handler error after {t_total:.2f}s: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': str(e)})
            }