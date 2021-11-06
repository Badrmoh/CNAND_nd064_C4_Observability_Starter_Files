from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics
from flask_opentracing import FlaskTracing
from jaeger_client import Config
from os import getenv

JAEGER_HOST = getenv('JAEGER_HOST', 'localhost')

app = Flask(__name__)
metrics = PrometheusMetrics(app)

# static information as metric
metrics.info('app_info', 'Application info', version='1.0.0')

metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

metrics.register_default(
    metrics.summary(
        'requests_by_status', 'Request latencies by status',
        labels={'status': lambda r: r.status_code}
    )
)

config = Config(
    config={
        'sampler':
        {'type': 'const',
         'param': 1},
        'logging': True,
        'reporter_batch_size': 1,
        'local_agent': {'reporting_host': JAEGER_HOST},},
        service_name="frontend")

jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer, True, app)

@app.route('/')
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()