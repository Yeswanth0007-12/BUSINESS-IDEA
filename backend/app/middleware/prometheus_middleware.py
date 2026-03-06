"""
Prometheus metrics middleware for FastAPI.
Collects and exposes metrics for monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time


# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

http_active_connections = Gauge(
    'http_active_connections',
    'Number of active HTTP connections'
)

celery_queue_length = Gauge(
    'celery_queue_length',
    'Number of tasks in Celery queue',
    ['queue']
)

celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total Celery tasks processed',
    ['task_type', 'status']
)

celery_task_duration_seconds = Histogram(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_type']
)

celery_active_workers = Gauge(
    'celery_active_workers',
    'Number of active Celery workers'
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for HTTP requests.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Increment active connections
        http_active_connections.inc()
        
        # Record start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()
            raise
            
        finally:
            # Decrement active connections
            http_active_connections.dec()


def metrics_endpoint():
    """
    Endpoint to expose Prometheus metrics.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def update_celery_metrics(celery_app):
    """
    Update Celery-related metrics.
    Should be called periodically.
    """
    try:
        # Get queue lengths
        inspect = celery_app.control.inspect()
        
        # Active tasks
        active = inspect.active()
        if active:
            total_active = sum(len(tasks) for tasks in active.values())
            celery_active_workers.set(len(active))
        
        # Queue lengths (requires Redis)
        from app.core.celery_app import celery_app as app
        from celery.result import AsyncResult
        
        # This is a simplified version - in production, you'd query Redis directly
        # for accurate queue depths
        
    except Exception as e:
        # Log error but don't fail
        print(f"Error updating Celery metrics: {e}")


def record_celery_task_start(task_name: str):
    """Record when a Celery task starts."""
    pass  # Metrics are recorded in task completion


def record_celery_task_completion(task_name: str, duration: float, status: str):
    """
    Record Celery task completion.
    
    Args:
        task_name: Name of the task
        duration: Task duration in seconds
        status: 'success' or 'failure'
    """
    celery_tasks_total.labels(
        task_type=task_name,
        status=status
    ).inc()
    
    celery_task_duration_seconds.labels(
        task_type=task_name
    ).observe(duration)
