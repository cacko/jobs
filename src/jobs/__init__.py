__name__ = "jobs"
__version__ = "0.1.0"

import corelog
import os


corelog.register(os.environ.get("JOBS_LOG_LEVEL", "INFO"))
