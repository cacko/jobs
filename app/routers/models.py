import datetime
from typing import Optional
from pydantic import BaseModel

from app.database.enums import JobEvent, JobStatus, LocationType, Source


class BaseResponse(BaseModel):

    def model_dump(self, **kwds):
        return super().model_dump(mode='json', **kwds)


class ImageReponse(BaseResponse):
    thumb_src: str
    webp_src: str
    raw_src: str


class CVResponse(BaseResponse):
    slug: str
    name: str
    image: ImageReponse
    added: datetime.datetime


class LocationResponse(BaseResponse):
    country_iso: str
    city: str


class JobEventResponse(BaseResponse):
    event: JobEvent
    description: str
    timestamp: datetime.datetime


class JobResponse(BaseResponse):
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
