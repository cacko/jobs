import questionary
from contextlib import contextmanager
from jobs.database.models.job import Job
from pydantic import BaseModel
from jobs.database.enums import JobStatus


class JobInput(BaseModel):
    job_id: str


@contextmanager
def select_job_form():
    jobs_choices = [
        questionary.Choice(title=job.job_name, value=job.slug)
        for job in Job.select().where(
            [Job.Status.not_in([JobStatus.REJECTED, JobStatus.EXPIRED])]
        ).order_by(-Job.last_modified)
    ]

    form = questionary.form(
        job_id=questionary.select("Job", choices=jobs_choices)
    )
    try:
        yield form
    except KeyboardInterrupt:
        return None
    finally:
        return None
