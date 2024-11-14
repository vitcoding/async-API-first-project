import logging
import multiprocessing

from core.logger import LOGGING

bind = '0.0.0.0:8000'
worker_class = 'uvicorn.workers.UvicornWorker'
workers = multiprocessing.cpu_count() * 2 + 1

log_config = LOGGING
log_level = logging.DEBUG
