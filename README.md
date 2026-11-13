# Redirector
Redirector is a simple Flask app that redirects resarch participants who click on a unmoderated usability testing link to their dedicated Grafana Cloud stack. 

This app was created from a template created by folks from [Render](https://render.com/).

## How it works

- `/` shows a landing page with a start button.
- `/go` redirects each participant to the next Grafana Cloud stack from `test-stacks.txt` (round-robin, wraps around after the last stack).
- `/metrics` exposes Prometheus metrics, including `ux_redirects_total`.

## OpenTelemetry

The app exports traces via OTLP. Point it at your backend with standard environment variables, e.g. for Grafana Cloud:

```text
OTEL_SERVICE_NAME=ux-redirector
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-<region>.grafana.net/otlp
OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic <base64(instance-id:token)>"
```

Without `OTEL_EXPORTER_OTLP_ENDPOINT` set, spans are printed to the console, which is useful for local development.
