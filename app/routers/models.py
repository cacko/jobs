import datetime
from typing import Optional
from pydantic import BaseModel

from app.database.fields import JobEvent, JobStatus, LocationType, Source


class ImageReponse(BaseModel):
    thumb_src: str
    webp_src: str
    raw_src: str


class CVResponse(BaseModel):
    slug: str
    name: str
    image: ImageReponse
    added: datetime.datetime


class LocationResponse(BaseModel):
    country_iso: str
    city: str


class JobEventResponse(BaseModel):
    event: JobEvent
    description: str
    timestamp: datetime.datetime


class JobResponse(BaseModel):
    position: str
    company: str
    id: str
    last_modified: datetime.datetime
    cv: CVResponse
    deleted: bool
    status: JobStatus
    location: LocationResponse
    onsite: LocationType
    source: Source
    events: Optional[list[JobEventResponse]] = None
