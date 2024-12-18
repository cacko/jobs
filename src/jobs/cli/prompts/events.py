import questionary
from contextlib import contextmanager
from jobs.database.enums import JobEvent, JobStatus
from jobs.database.models.job import Job
from pydantic import BaseModel


class EventInput(BaseModel):
    job_id: str
    event: JobEvent
    description: str


@contextmanager
def add_event_form():
    jobs_choices = [
        questionary.Choice(title=job.job_name, value=job.slug)
        for job in Job.select().where(
            [Job.Status.not_in([JobStatus.REJECTED, JobStatus.EXPIRED])]
        )
    ]

    form = questionary.form(
        job_id=questionary.select("Job", choices=jobs_choices),
        event=questionary.select("Event", choices=JobEvent.values()),
        description=questionary.text("Description", multiline=True),
    )
    try:
        yield form
    except KeyboardInterrupt:
        return None
    finally:
        return None
