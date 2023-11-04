from pathlib import Path
import typer
from app.database.fields import JobStatus, LocationType, Source
from app.database.models.position import Position
from app.main import serve
from app.database import create_tables
from app.database.models import (
    Company,
    CV,
    Location,
    Job
)
from typing_extensions import Annotated
from app.core.pdf import to_pil
from coreimage.terminal import get_kitty_image as get_term_image
import logging

from app.core.country import to_iso

cli = typer.Typer()


@cli.command()
def serve_api():
    serve()


@cli.command()
def init_db():
    create_tables()


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
def add_job(
    company: Annotated[str, typer.Option()],
    position: Annotated[str, typer.Option()],
    city: Annotated[str, typer.Option()],
    url:  Annotated[str, typer.Option()],
    cv:  Annotated[Path, typer.Option()],
    status: Annotated[JobStatus, typer.Option()] = JobStatus.PENDING,
    country: Annotated[str, typer.Option()] = "gb",
    source: Annotated[Source, typer.Option()] = Source.LINKEDIN,
    site: Annotated[LocationType, typer.Option()] = LocationType.HYBRID
):
    location_obj, _ = Location.get_or_create(
        country_iso=to_iso(country),
        city=city
    )
    position_obj, _ = Position.get_or_create(name=position)
    cv_obj = CV.from_path(cv)
    company_obj, _ = Company.get_or_create(name=company)

    job, created = Job.get_or_create(
        Source=source,
        Company=company_obj,
        OnSiteRemote=site,
        Location=location_obj,
        CV=cv_obj,
        Status=status,
        ad_url=url,
        Position=position_obj
    )

    logging.debug(f"Created: {created}")
    logging.info(f"\n{job.to_table()}")


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if not ctx.invoked_subcommand:
        ctx.invoke(serve_api)


if __name__ == '__main__':
    cli()
