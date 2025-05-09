from typing import Optional
import questionary
from contextlib import contextmanager
from jobs.database.enums import CV_PATH, CL_PATH, JobStatus, LocationType, Source
from pycountry import countries
from jobs.database.models.company import Company
from jobs.database.models.location import Location
from jobs.database.models.position import Position
from pydantic import BaseModel, field_validator
from pathlib import Path
from . import THEME
from urllib.parse import urlparse


class ApplyInput(BaseModel):
    company: str
    position: str
    city: str
    url: str
    cv_path: Path
    note: str
    status: JobStatus
    country: str
    source: Source
    site: LocationType
    cover_letter_path: Path

    @property
    def cv(self) -> Path:
        return Path(CV_PATH) / self.cv_path

    @property
    def cover_letter(self) -> Path:
        return Path(CL_PATH) / self.cover_letter_path

    @field_validator("url")
    @classmethod
    def clean_url(cls, url: str):
        return urlparse(url)._replace(query="", fragment="").geturl()


@contextmanager
def apply_job_form():
    form = questionary.form(
        company=questionary.autocomplete(
            "Company", choices=Company.get_names(), style=THEME
        ),
        position=questionary.autocomplete("Position", choices=Position.get_names()),
        city=questionary.autocomplete("City", choices=Location.get_cities()),
        url=questionary.text("Url"),
        cv_path=questionary.path(
            "CV",
            get_paths=lambda: [CV_PATH],
            file_filter=lambda f: f.lower().endswith(".pdf"),
        ),
        cover_letter_path=questionary.path("Cover Letter", get_paths=lambda: [CL_PATH]),
        note=questionary.text("Application Note", multiline=True),
        status=questionary.select(
            "Status",
            choices=JobStatus.values(),
            default=JobStatus.PENDING.value,
        ),
        country=questionary.autocomplete(
            "Country", choices=[cnt.name for cnt in countries], default="United Kingdom"
        ),
        source=questionary.select(
            "Source",
            choices=Source.values(),
            default=Source.LINKEDIN.value,
        ),
        site=questionary.select(
            "OnSite/Remote",
            choices=LocationType.values(),
            default=LocationType.HYBRID.value,
        ),
    )
    try:
        yield form
    except KeyboardInterrupt:
        return None
    finally:
        return None
