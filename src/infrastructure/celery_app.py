import os
from celery import Celery

# RabbitMQ Broker:
# amqp://user:password@host:port//
BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

# Redis db: store results/status
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "cryptoflow_worker",
    broker=BROKER_URL,
    backend=BACKEND_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # "acks_late": Only confirm task is done AFTER execution finishes.
    # If worker crashes mid-task, the task is re-queued.
    task_acks_late=True,
)

# Auto-discover tasks in the application layer
celery_app.autodiscover_tasks(["src.application.tasks"])