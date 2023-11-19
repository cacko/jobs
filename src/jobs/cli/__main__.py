from pathlib import Path
import rich
import typer
from jobs.main import serve
from jobs.database import create_tables
from jobs.database.models import (
    Company,
    CV,
    Location,
    Job,
)
from typing_extensions import Annotated
from jobs.core.pdf import to_pil
from coreimage.terminal import get_kitty_image as get_term_image
import logging
from .prompts.jobs import ApplyInput, apply_job_form
from .prompts.events import EventInput, add_event_form
from .prompts.job import JobInput, select_job_form
from jobs.core.country import to_iso
from jobs.cli.commands.job import (
    cmd_apply,
    cmd_event,
    cmd_tokens
)
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
        cmd_apply(input)


@cli.command()
def event():
    with add_event_form() as form:
        ans = form.ask()
        input = EventInput(**ans)
        cmd_event(input=input)


@cli.command()
def tokens():
    with select_job_form() as form:
        ans = form.ask()
        input = JobInput(**ans)
        cmd_tokens(input=input)


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
