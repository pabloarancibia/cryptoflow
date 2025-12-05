import time
import structlog
import os
import redis
from src.infrastructure.celery_app import celery_app

logger = structlog.get_logger()

# Setup a synchronous Redis client specifically for the Worker
# We use the same URL as the cache, but a blocking client
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@celery_app.task(name="tasks.handle_order_created")
def handle_order_created(order_id: str, symbol: str, price: float):
    """
    Consumer Logic: This runs in the BACKGROUND PROCESS.
    Idempotent Consumer.
    Ensures that even if RabbitMQ delivers this message 5 times,
    we only execute the logic once.
    """

    idempotency_key = f"processed_event:{order_id}"

    # Check if key exists (Atomic Lock)
    # .setnx() = SET if Not eXists. Returns True if set, False if already there.
    # We set a TTL (Time To Live) of 24 hours. After that, we assume duplicate risks are gone.
    is_new_event = redis_client.set(idempotency_key, "1", nx=True, ex=86400)

    if not is_new_event:
        logger.warning("duplicate_event_detected", order_id=order_id, status="SKIPPED")
        return "Duplicate skipped"

    # ----------------------------------------------------
    # CORE LOGIC (Only runs if is_new_event is True)
    # ----------------------------------------------------
    logger.info("worker_processing_task", task="handle_order_created", order_id=order_id)

    # Simulate complex processing (e.g., Sending Email, Reporting to SEC)
    time.sleep(2)  # Sleep to prove it doesn't block the API

    logger.info("worker_task_complete", order_id=order_id, status="PROCESSED")

    return f"Order {order_id} processed successfully."