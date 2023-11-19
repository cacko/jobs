from pathlib import Path
import rich
import typer
from jobs.database.fields import JobEvent, JobStatus
from jobs.database.models.position import Position
from jobs.database.models.skill import Skill
from jobs.main import serve
from jobs.database import create_tables
from jobs.database.models import (
    Company,
    CV,
    Location,
    Job,
    Event
)
from typing_extensions import Annotated
from jobs.core.pdf import to_pil
from coreimage.terminal import get_kitty_image as get_term_image
import logging
from jobs.masha.skills import Skills
from jobs.prompts.jobs import ApplyInput, apply_job_form
from jobs.prompts.events import EventInput, add_event_form
from jobs.prompts.job import JobInput, select_job_form
from itertools import groupby
from humanfriendly.tables import format_robust_table
from jobs.core.country import to_iso

cli = typer.Typer()


@cli.command()
def serve_api():
    serve()


@cli.command()
def init_db():
    try:
        assert typer.confirm("Dropping all data?")
        create_tables(drop=True)
    except AssertionError:
        logging.info("ignored")


@cli.command()
def pdf2img(pdf: Annotated[Path, typer.Argument()]):
    img = to_pil(pdf)
    print(get_term_image(image=img, height=40))


@cli.command()
def add_company(name: str):
    company, created = Company.get_or_create(
        name=name
    )
    logging.debug(f"Created: {created}")
    logging.info(f"\n{company.to_table()}")


@cli.command()
def add_cv(cv_path: Annotated[Path, typer.Argument()]):
    cv = CV.from_path(cv_path)
    logging.info(f"\n{cv.to_table()}")


@cli.command()
def add_location(country: str, city: str):
    location, created = Location.get_or_create(
        country_iso=to_iso(country),
        city=city
    )
    logging.debug(f"Created: {created}")
    logging.info(f"\n{location.to_table()}")


@cli.command()
def apply():
    with apply_job_form() as form:
        ans = form.ask()
        input = ApplyInput(**ans)
        logging.debug(input)
        location_obj, _ = Location.get_or_create(
            country_iso=to_iso(input.country),
            city=input.city
        )
        position_obj, _ = Position.get_or_create(name=input.position)
        cv_obj = CV.from_path(input.cv)
        company_obj, _ = Company.get_or_create(name=input.company)

        job, created = Job.get_or_create(
            Source=input.source,
            Company=company_obj,
            OnSiteRemote=input.site,
            Location=location_obj,
            CV=cv_obj,
            Status=input.status,
            url=input.url,
            Position=position_obj
        )

        logging.debug(f"Created: {created}")
        logging.info(f"\n{job.to_table()}")

        event, created = Event.get_or_create(
            Job=job,
            Event=JobEvent.APPLIED,
            description=input.note
        )

        logging.debug(f"Created: {created}")
        logging.info(f"\n{event.to_table()}")


@cli.command()
def event():
    with add_event_form() as form:
        ans = form.ask()
        input = EventInput(**ans)
        job: Job = Job.get(Job.slug == input.job_id)
        event, created = Event.get_or_create(
            Job=job,
            Event=input.event,
            description=input.description
        )
        logging.info(f"{event} created={created}")
        match input.event:
            case JobEvent.REJECT:
                job.Status = JobStatus.REJECTED
            case JobEvent.APPLIED:
                job.Status = JobStatus.PENDING
            case _:
                job.Status = JobStatus.IN_PROGRESS
        job.save()
        logging.debug(f"Changaing job status to {job.Status}")


@cli.command()
def tokens():
    with select_job_form() as form:
        ans = form.ask()
        input = JobInput(**ans)
        job: Job = Job.get(Job.slug == input.job_id)
        apply: Event = Event.get(Event.Job == job, Event.Event == JobEvent.APPLIED)
        skills = sorted(Skills(apply.description).result, key=lambda s: s.entity_group)
        columns = []
        row = []
        for k, g in groupby(skills, key=lambda s: s.entity_group):
            columns.append(k)
            row.append(",".join([t.word for t in g]))
        print(format_robust_table([row], columns))
        if typer.confirm("update skills?"):
            job.skills.clear()
            new_skills = [Skill.get_or_create(
                Group=token.entity_group,
                name=token.word
            )[0] for token in skills]
            rich.print(new_skills)
            job.skills.add(new_skills)


@cli.command()
def job():
    with select_job_form() as form:
        ans = form.ask()
        input = JobInput(**ans)
        job: Job = Job.get(Job.slug == input.job_id)
        rich.print(job.to_response())


@cli.command()
def menu(ctx: typer.Context):
    pass


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if not ctx.invoked_subcommand:
        ctx.invoke(menu)


if __name__ == '__main__':
    cli()
