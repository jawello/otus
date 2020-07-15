from typing import Callable, Awaitable
from prometheus_client import Counter, Gauge, Histogram, CONTENT_TYPE_LATEST
import time
from aiohttp import web
import prometheus_client

app_name_metrics = None


@web.middleware
async def prom_middleware(request: web.Request, handler: Callable[[web.Request], Awaitable[web.StreamResponse]]) \
        -> web.StreamResponse:
    try:
        request['start_time'] = time.time()
        request.app['REQUEST_IN_PROGRESS'].labels(
            app_name_metrics, request.path, request.method).inc()
        response = await handler(request)
        resp_time = time.time() - request['start_time']
        request.app['REQUEST_LATENCY'].labels(app_name_metrics, request.path).observe(resp_time)
        request.app['REQUEST_IN_PROGRESS'].labels(app_name_metrics, request.path, request.method).dec()
        request.app['REQUEST_COUNT'].labels(
            app_name_metrics, request.method, request.path, response.status).inc()
        return response
    except Exception as ex:
        raise


async def metrics(request):
    resp = web.Response(body=prometheus_client.generate_latest())
    resp.content_type = CONTENT_TYPE_LATEST
    return resp


def setup_metrics(app, app_name):
    app['REQUEST_COUNT'] = Counter(
      'requests_total', 'Total Request Count',
      ['app_name', 'method', 'endpoint', 'http_status']
    )
    app['REQUEST_LATENCY'] = Histogram(
        'request_latency_seconds', 'Request latency',
        ['app_name', 'endpoint']
    )

    app['REQUEST_IN_PROGRESS'] = Gauge(
        'requests_in_progress_total', 'Requests in progress',
        ['app_name', 'endpoint', 'method']
    )
    global app_name_metrics
    app_name_metrics = app_name
    app.middlewares.insert(0, prom_middleware)
    app.router.add_get("/metrics", metrics)

