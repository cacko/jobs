__name__ = "jobs"

import corelog
import os


corelog.register(os.environ.get("JOBS_LOG_LEVEL", "INFO"))
