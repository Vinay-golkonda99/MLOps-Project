import os
import configparser
import logging
from transformers import LlamaTokenizer, AutoModelForCausalLM, pipeline

def setup_logging(config_file='logging.ini'):
    config = configparser.ConfigParser()
    config.read(config_file)

    loggers = {
        'logger1': config.get('logging', 'Api'),
        'logger2': config.get('logging', 'Api_error')
    }

    log_levels = {
        'logger1': config.get('logging', 'level1'),
        'logger2': config.get('logging', 'level2')
    }

    for log, filename in loggers.items():
        logger = logging.getLogger(log)
        logger.setLevel(getattr(logging, log_levels[log]))

        handler = logging.FileHandler(filename)
        handler.setLevel(getattr(logging, log_levels[log]))

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logging.getLogger('logger1'), logging.getLogger('logger2')


def get_model(logger1, logger2):
    CACHE_DIR = "./model_cache"
    model_path = os.getenv("MODEL_PATH", "/mnt/models/Deepseek") 
    logger1.info(f"modelpath : {model_path}")
    
    if not os.path.exists(model_path):
        logger2.error("no model path")
        raise FileNotFoundError(f"Model path does not exist: {model_path}")

    try:
        tokenizer = LlamaTokenizer.from_pretrained(model_path, cache_dir=CACHE_DIR)
        logger1.info(f"tokenizer loaded successfully")
    except Exception as e:
        logger2.error(f"Tokenizer loading failed: {e}")
        raise

    try:
        model = AutoModelForCausalLM.from_pretrained(model_path, cache_dir=CACHE_DIR)
        logger1.info(f"model loaded successfully")
    except Exception as e:
        logger2.error(f"Model loading failed: {e}")
        raise

    generator = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)
    return tokenizer, model, generator
