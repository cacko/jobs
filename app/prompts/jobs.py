import logging
import questionary
from contextlib import contextmanager
from app.database.enums import CV_PATH, JobStatus, LocationType, Source
from pycountry import countries
from app.database.models.company import Company
from app.database.models.location import Location
from app.database.models.position import Position
from pydantic import BaseModel
from pathlib import Path


class ApplyInput(BaseModel):
    company: str
    position: str
    city: str
    url:  str
    cv_path:  Path
    note: str
    status: JobStatus
    country: str
    source: Source
    site: LocationType

    @property
    def cv(self) -> Path:
        return Path(CV_PATH) / self.cv_path


@contextmanager
def apply_job_form():

    form = questionary.form(
        company=questionary.autocomplete(
            "Company", choices=Company.get_names()),
        position=questionary.autocomplete(
            "Position", choices=Position.get_names()),
        city=questionary.autocomplete(
            "City", choices=Location.get_cities()),
        url=questionary.text(
            "Url"
        ),
        cv_path=questionary.path(
            "CV",
            get_paths=lambda: [CV_PATH]
        ),
        note=questionary.text(
            "Application Note",
            multiline=True
        ),
        status=questionary.select(
            "Status",
            choices=JobStatus.values(),
            default=JobStatus.PENDING.value
        ),
        country=questionary.autocomplete(
            "Country",
            choices=[cnt.name for cnt in countries],
            default="United Kingdom"
        ),
        source=questionary.select(
            "Source",
            choices=Source.values(),
            default=Source.LINKEDIN.value
        ),
        site=questionary.select(
            "OnSite/Remote",
            choices=LocationType.values(),
            default=LocationType.HYBRID.value
        ),

    )
    try:
        yield form
    except Exception as e:
        logging.exception(e)
    finally:
        return None
