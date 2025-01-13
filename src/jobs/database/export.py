from pathlib import Path
import pandas as pd
from jobs.database.enums import JobEvent
from jobs.database.models import Job, Event
import rich
from corefile import TempPath
from datetime import datetime, timezone

id_to_pos = {}


def to_xlsx() -> Path:

    data = {
        'Company': [],
        'Position': [],
        'Location': [],
        'Url': [],
        'Applied': [],
        'Status': [],
        'Last Response': []
    }

    filters = [Event.Event == JobEvent.APPLIED]
    # order_by = []

    base_query = Event.select().join_from(Event, Job)
    query = base_query.where(*filters)

    for idx, event in enumerate(query):
        job: Job = event.Job
        id_to_pos.setdefault(job.slug, idx)
        data["Company"].append(job.Company.name)
        data["Position"].append(job.Position.name)
        data["Location"].append(f"{job.Location.name}")
        data["Url"].append(job.url)
        data['Status'].append(job.Status.value.upper())
        data['Applied'].append(event.timestamp)
        data['Last Response'].append(job.last_modified)

    df = pd.DataFrame(data)

    now = int(datetime.now(tz=timezone.utc).timestamp())
    tmp_path = TempPath(f"jobs{now}.xlsx")

    df.to_excel(tmp_path.as_posix())
    return tmp_path
