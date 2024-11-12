import logging
import os
from logging import config as logging_config

from core.logger import LOGGING

# Настройки логирования
logging_config.dictConfig(LOGGING)

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv("PROJECT_NAME", "movies")

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

# Настройки Elasticsearch
ELASTIC_SCHEMA = os.getenv("ELASTIC_SCHEMA", "http://")
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "127.0.0.1")
ELASTIC_PORT = int(os.getenv("ELASTIC_PORT", 9200))

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Настройки дополнительного логера для дебага
format_log = (
    "#%(levelname)-8s [%(asctime)s] - %(filename)s:"
    "%(lineno)d - %(name)s - %(message)s"
)
logging.basicConfig(
    level=logging.INFO,
    format=format_log,
)
log = logging.getLogger("DEBUG_LOG")
