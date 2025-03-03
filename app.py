import os
from flask import Flask, redirect
from multiprocessing import Value
from prometheus_flask_exporter import PrometheusMetrics
import random

# Initiate a counter named 'counter'
counter = Value('i', 0)

# Open a 'test-stacks.txt' file with a list of test stacks
file = open("test-stacks.txt", "r")

# Read the test stacks file into a list called 'stacks'
with open('test-stacks.txt') as f:
    stacks = f.read().splitlines()

# Start the app
app = Flask(__name__)
metrics = PrometheusMetrics(app)

# Metrics
stacks_number = metrics.info('test_stacks_total', 'Number of test stacks')
stacks_number.set(len(stacks))

# If the url has path '/' (no path)
@app.route('/')
def hello():
    with counter.get_lock():
            # Create a string called 'url' as a connection of 'https://', stack name and '.grafana.net'
            url = f'https://{stacks[counter.value]}.grafana.net/d/e01fc5f7-d567-4631-9fa1-192ef1d88497/login-service-dashboard?orgId=1'
            # Increase counter by 1
            counter.value += 1
    # Redirect to the url
    print("A participant was redirected to", url)
    return redirect(url, code=302) 

if __name__ == '__app__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
