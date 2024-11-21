import logging

# Logger for debug
format_log = (
    "#%(levelname)-8s [%(asctime)s] - %(filename)s:"
    "%(lineno)d - %(name)s - %(message)s"
)
logging.basicConfig(
    level=logging.DEBUG,
    format=format_log,
)
log = logging.getLogger("DEBUG_LOG")
