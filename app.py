import os
from flask import Flask, redirect, render_template
from multiprocessing import Value
from prometheus_flask_exporter import PrometheusMetrics

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

DASHBOARD_PATH = '/d/e01fc5f7-d567-4631-9fa1-192ef1d88497/login-service-dashboard?orgId=1'

# Initiate a counter named 'counter'
counter = Value('i', 0)

# Read the test stacks file into a list called 'stacks'
with open('test-stacks.txt') as f:
    stacks = f.read().splitlines()

# Start the app
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Tracing: export via OTLP when an endpoint is configured, log to console otherwise
resource = Resource.create({'service.name': 'ux-redirector'})
tracer_provider = TracerProvider(resource=resource)
if os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT'):
    exporter = OTLPSpanExporter()
else:
    exporter = ConsoleSpanExporter()
tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(tracer_provider)
FlaskInstrumentor().instrument_app(app, tracer_provider=tracer_provider)
tracer = trace.get_tracer(__name__)

# Metrics
stacks_number = metrics.info('test_stacks_total', 'Number of test stacks')
stacks_number.set(len(stacks))

# Landing page for research participants
@app.route('/')
def index():
    with tracer.start_as_current_span('landing_page') as span:
        span.set_attribute('ux.stacks.total', len(stacks))
        return render_template('index.html', stacks_total=len(stacks))

# Round-robin redirect to the participant's dedicated Grafana Cloud stack
@app.route('/go')
@metrics.counter('ux_redirects_total', 'Number of participants redirected')
def redirect_to_stack():
    with counter.get_lock():
        stack_index = counter.value % len(stacks)
        participant_number = counter.value + 1
        counter.value += 1
    stack = stacks[stack_index]
    url = f'https://{stack}.grafana.net{DASHBOARD_PATH}'
    span = trace.get_current_span()
    span.set_attribute('ux.stack.name', stack)
    span.set_attribute('ux.stack.index', stack_index)
    span.set_attribute('ux.participant.number', participant_number)
    print("A participant was redirected to", url)
    return redirect(url, code=302)

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
