import os
from flask import request, jsonify, Flask
from config import setup_logging

# ✅ OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# ✅ Prometheus Metrics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# ✅ Transformers
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer, AutoModelForCausalLM

# Tracing setup
trace.set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "llm-flask-service"}))
)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://tempo.monitoring.svc.cluster.local:4318/v1/traces",
    insecure=True
)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
tracer = trace.get_tracer(__name__)

# Flask setup
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# ✅ Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency', ['endpoint'])

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


# ✅ Dynamic model loader
def get_model(logger1, logger2):
    model_dir = "/mnt/models/Deepseek"

    if not os.path.exists(model_dir):
        logger1.info("Downloading model from Hugging Face...")
        snapshot_download(
            repo_id='BEE-spoke-data/smol_llama-101M-GQA',
            local_dir=model_dir,
            local_dir_use_symlinks=False
        )

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForCausalLM.from_pretrained(model_dir)

    def generator(prompt, **kwargs):
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids
        output_ids = model.generate(input_ids, **kwargs)
        return tokenizer.batch_decode(output_ids, skip_special_tokens=True)

    return tokenizer, model, generator


@app.route('/ask_bot', methods=['GET'])
def generate_sql():
    logger1, logger2 = setup_logging()
    REQUEST_COUNT.labels(method='GET', endpoint='/ask_bot').inc()

    with REQUEST_LATENCY.labels(endpoint='/ask_bot').time():
        logger1.info("Inside /ask_bot endpoint")

        with tracer.start_as_current_span("generate_sql_route"):
            try:
                tokenizer, model, generator = get_model(logger1, logger2)
                logger1.info("Model and tokenizer loaded successfully")

                model_size = sum(p.numel() for p in model.parameters()) / 1e6
                logger1.info(f"Model size: {model_size:.2f} million parameters")

                prompt = request.args.get("prompt", "Write an SQL query to list all employees in the HR department.")
                logger1.info(f"Generating text for prompt: {prompt}")

                with tracer.start_as_current_span("model_generation"):
                    generated_text = generator(prompt, max_length=100, num_return_sequences=1)[0]

                return jsonify({
                    "prompt": prompt,
                    "output": generated_text,
                    "model_size_million_params": model_size
                })

            except Exception as e:
                logger2.error(f"Exception occurred: {e}", exc_info=True)
                return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1999)
