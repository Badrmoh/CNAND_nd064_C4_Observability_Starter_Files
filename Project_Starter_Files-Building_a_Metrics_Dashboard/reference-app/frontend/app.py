from flask import Flask, render_template, request
from prometheus_flask_exporter import PrometheusMetrics

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

@app.route('/')
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()