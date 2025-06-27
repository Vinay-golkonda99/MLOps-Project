import os
from flask import request, jsonify, Flask
from config import setup_logging, get_model

app = Flask(__name__)

@app.route('/ask_bot', methods=['GET'])
def generate_sql():
    logger1, logger2 = setup_logging()
    logger1.info("Inside /ask_bot endpoint")

    try:
        # Load model and tokenizer
        tokenizer, model, generator = get_model(logger1, logger2)
        logger1.info("Model and tokenizer loaded successfully")

        model_size = sum(p.numel() for p in model.parameters()) / 1e6
        logger1.info(f"Model size: {model_size:.2f} million parameters")

        # Use a default prompt
        prompt = request.args.get("prompt", "Write an SQL query to list all employees in the HR department.")

        logger1.info(f"Generating text for prompt: {prompt}")
        output = generator(prompt, max_length=100, num_return_sequences=1)[0]['generated_text']

        return jsonify({
            "prompt": prompt,
            "output": output,
            "model_size_million_params": model_size
        })

    except Exception as e:
        logger2.error(f"Exception occurred: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run Flask on port 9091
    app.run(host='0.0.0.0', port=9091)
