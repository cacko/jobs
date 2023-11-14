from datetime import datetime, timezone
from typing import Optional
from pydantic import AwareDatetime, BaseModel

from jobs.database.enums import JobEvent, JobStatus, LocationType, Source


class BaseResponse(BaseModel):

    def __init__(self, *args, **kwds):
        for k, v in kwds.items():
            match v:
                case datetime():
                    kwds[k] = v.astimezone(tz=timezone.utc)
        super().__init__(*args, **kwds)

    def model_dump(self):
        return super().model_dump(mode='json')


class CompanyResponse(BaseResponse):
    name: str
    url: Optional[str] = None


class ImageReponse(BaseResponse):
    thumb_src: str
    webp_src: str
    raw_src: str


class CVResponse(BaseResponse):
    slug: str
    name: str
    image: ImageReponse
    added: AwareDatetime


class LocationResponse(BaseResponse):
    country_iso: str
    city: str


class JobEventResponse(BaseResponse):
    event: JobEvent
    description: str
    timestamp: AwareDatetime


class JobResponse(BaseResponse):
    position: str
    company: CompanyResponse
    id: str
    last_modified: AwareDatetime
    cv: CVResponse
    deleted: bool
    status: JobStatus
    location: LocationResponse
    onsite: LocationType
    source: Source
    url: str
    events: Optional[list[JobEventResponse]] = None
