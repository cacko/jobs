__name__ = "jobs"

from datetime import datetime, timezone
import corelog
import os

from jobs.firebase.db import UpdatesDb


corelog.register(os.environ.get("JOBS_LOG_LEVEL", "INFO"))
