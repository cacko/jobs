import questionary
from contextlib import contextmanager
from jobs.database.enums import JobEvent, JobStatus
from jobs.database.models.job import Job
from jobs.database.models.event import Event
from pydantic import BaseModel


class EventInput(BaseModel):
    job_id: str
    event: JobEvent
    description: str


class EventIdInput(BaseModel):
    event_id: int


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


@contextmanager
def delete_event_form():
    jobs_choices = [
        questionary.Choice(title=job.job_name, value=job.slug)
        for job in Job.select().where(
            [Job.Status.not_in([JobStatus.REJECTED, JobStatus.EXPIRED])]
        )
    ]
    form1 = questionary.form(
        job_id=questionary.select("Job", choices=jobs_choices),
    )
    ans = form1.ask()
    job: Job = Job.get(Job.slug == ans["job_id"])
    events: list[Event] = Event.select().where(Event.Job == job)
    form = questionary.form(
        event_id=questionary.select(
            f"{job.job_name} Events",
            choices=[
                questionary.Choice(title=f"{e.Event} {e.timestamp}", value=e.id)
                for e in events
            ],
        ),
    )
    try:
        yield form
    except KeyboardInterrupt:
        return None
    finally:
        return None
