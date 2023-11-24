import logging
import questionary
from contextlib import contextmanager
from jobs.database.models.job import Job
from pydantic import BaseModel


class JobInput(BaseModel):
    job_id: str


@contextmanager
def select_job_form():
    jobs_choices = [
        questionary.Choice(title=job.job_name, value=job.slug) for job in Job.select()
    ]

    form = questionary.form(
        job_id=questionary.select("Job", choices=jobs_choices, use_shortcuts=True)
    )
    try:
        yield form
    except KeyboardInterrupt:
        return None
    finally:
        return None
