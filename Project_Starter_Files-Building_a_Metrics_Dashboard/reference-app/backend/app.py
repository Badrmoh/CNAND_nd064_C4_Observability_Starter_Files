from flask import Flask, render_template, request, jsonify

import pymongo
from flask_pymongo import PyMongo
from prometheus_flask_exporter import PrometheusMetrics
from flask_opentracing import FlaskTracing
from jaeger_client import Config

app = Flask(__name__)
metrics = PrometheusMetrics(app)

app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'

config = Config(
    config={
        'sampler':
        {'type': 'const',
         'param': 1},
        'logging': True,
        'reporter_batch_size': 1,},
        service_name="service")

jaeger_tracer = config.initialize_tracer()
tracing = FlaskTracing(jaeger_tracer, True, app)

mongo = PyMongo(app)

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
    return "Hello World"


@app.route('/api')
def my_api():
    answer = "something"
    return jsonify(repsonse=answer)

@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

if __name__ == "__main__":
    app.run()
