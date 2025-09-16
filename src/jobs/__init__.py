__name__ = "jobs"

import corelog
import logging
import os


corelog.register(os.environ.get("JOBS_LOG_LEVEL", "INFO"))
logging.getLogger("peewee").setLevel(os.environ.get("JOBS_LOG_LEVEL", "INFO"))
logging.getLogger("uvicorn").setLevel(os.environ.get("JOBS_LOG_LEVEL", "INFO"))