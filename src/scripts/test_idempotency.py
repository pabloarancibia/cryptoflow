import sys
from pathlib import Path
import uuid

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.application.tasks import handle_order_created


def test_idempotency():
    # Generate a single Order ID
    fixed_order_id = str(uuid.uuid4())
    print(f"--- Testing Idempotency for Order ID: {fixed_order_id} ---")

    print("[1] Sending First Task...")
    handle_order_created.delay(
        order_id=fixed_order_id,
        symbol="BTC",
        price=50000.0
    )

    print("[2] Sending Second Task (Duplicate)...")
    handle_order_created.delay(
        order_id=fixed_order_id,
        symbol="BTC",
        price=50000.0
    )

    print("--- Tasks Sent. Check Worker Logs! ---")


if __name__ == "__main__":
    test_idempotency()