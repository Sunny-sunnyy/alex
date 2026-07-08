#!/usr/bin/env python3
"""
Simple test for Tagger agent — OpenAI model.
"""

import time
import json
from dotenv import load_dotenv

load_dotenv(override=True)

from lambda_handler import lambda_handler
from agent import MODEL_ID

def test_tagger():
    """Test the tagger agent with unknown instruments"""

    test_event = {
        "instruments": [
            {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF"}
        ]
    }

    print("Testing Tagger Agent...")
    print(f"Model: {MODEL_ID}")
    print("=" * 60)

    t_start = time.monotonic()
    result = lambda_handler(test_event, None)
    t_total = time.monotonic() - t_start

    print(f"Status Code: {result['statusCode']}")

    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print(f"Tagged: {body.get('tagged', 0)} instruments")
        print(f"Updated: {body.get('updated', [])}")
        timing = body.get('timing', {})
        if timing:
            print(f"Timing: classify={timing.get('classify_s')}s, "
                  f"db={timing.get('db_s')}s, "
                  f"lambda_total={timing.get('lambda_total_s')}s")
        if body.get('classifications'):
            for c in body['classifications']:
                print(f"  {c['symbol']}: {c['type']}")
    else:
        print(f"Error: {result['body']}")

    print(f"Wall-clock total: {t_total:.2f}s")
    print("=" * 60)

if __name__ == "__main__":
    test_tagger()