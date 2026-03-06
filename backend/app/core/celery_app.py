"""
Celery application configuration for asynchronous task processing.
"""
from celery import Celery
from app.core.config import settings

# Initialize Celery application
celery_app = Celery(
    "packoptima",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    
    # Result expiration (24 hours)
    result_expires=86400,
    
    # Timezone
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.tasks.optimization_tasks.*": {"queue": "optimization"},
        "app.tasks.bulk_tasks.*": {"queue": "bulk"},
    },
    
    # Task priorities
    task_default_priority=5,
    
    # Worker configuration
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Task tracking
    task_track_started=True,
    task_send_sent_event=True,
)

# Auto-discover tasks from all registered apps
celery_app.autodiscover_tasks(["app.tasks"])
