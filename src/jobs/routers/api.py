import logging
from math import ceil, floor
from typing import Optional
from urllib.parse import urlencode
from fastapi import APIRouter, HTTPException, Request, Form, File, Depends
from jobs.database.enums import JobEvent, JobStatus
from jobs.database.models import Job, Event, User
from jobs.database.export import to_xlsx
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
from peewee import fn
from jobs.routers.models import EventRequest
from .auth import check_auth, check_admin
from jobs.config import app_config

router = APIRouter()


def get_list_response(
    email: str, page: int = 1, limit: int = 50, last_modified: Optional[datetime] = None
):
    
    results = []
    filters = [Job.User.email == email]
    if last_modified:
        filters.append(fn.date_trunc("second", Job.last_modified) > last_modified)
    # order_by = []

    query = Job.select().join(User)
    if len(filters):
        query = query.where(*filters)
    total = query.count()
    if total > 0:
        page = min(max(1, page), floor(total / limit) + 1)
    jobs = query.paginate(page, limit)
    events = Event.select().where(Event.Job.in_(jobs))
    results = [
        job.to_response(
            events=[
                event.to_response()
                for event in filter(lambda e: e.Job.id == job.id, events)
            ]
        ).model_dump()
        for job in jobs
    ]
    headers = {
        "x-pagination-total": f"{total}",
        "x-pagination-page": f"{page}",
    }

    def get_next_url(email: str, page: int, total: int, limit: int):
        try:
            last_page = ceil(total / limit)
            page += 1
            assert last_page + 1 > page
            params = {
                k: v
                for k, v in dict(
                    page=page,
                    limit=limit,
                ).items()
                if v
            }
            return f"{app_config.api.web_host}/api/jobs/{email}?{urlencode(params)}"
        except AssertionError:
            return None

    if next_url := get_next_url(
        email=email,
        total=total,
        page=page,
        limit=limit,
    ):
        headers["x-pagination-next"] = next_url
    return JSONResponse(content=results, headers=headers)


@router.get("/api/jobs/{email}", tags=["api"])
def list_jobs(
    email: str,
    page: int = 1,
    limit: int = 30,
    last_modified: Optional[datetime] = None,
    auth_user=Depends(check_auth),
):
    return get_list_response(
        email=email, page=page, limit=limit, last_modified=last_modified
    )


@router.get("/api/job/{email}/{slug}", tags=["api"])
def get_job(email: str, slug: str, auth_user=Depends(check_auth)):
    try:
        job: Job = Job.select(Job).where(Job.slug == slug).get()
        assert job
        events = Event.select(Event).where(Event.Job == job)
        response = job.to_response(events=[e.to_response() for e in events])
        return JSONResponse(content=response.model_dump())
    except AssertionError:
        raise HTTPException(404)


@router.get("/api/jobs/{email}.xlsx", tags=["api"])
def xlsx_export(enail: str, auth_user=Depends(check_auth)):
    xlsx_path = to_xlsx()
    assert xlsx_path.exists()
    return FileResponse(
        path=xlsx_path.as_posix(),
        filename=xlsx_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.put("/api/events/{email}", tags=["api"])
def add_job_event(
    email: str, input: EventRequest, auth_user=Depends(check_auth)
):
    job: Job = Job.get(Job.slug == input.job_id, Job.User == auth_user)
    assert job
    event, created = Event.get_or_create(
        Job=job, Event=input.event, description=input.description
    )
    assert event
    match event.Event:
        case JobEvent.REJECT:
            job.Status = JobStatus.REJECTED
        case JobEvent.APPLIED:
            job.Status = JobStatus.PENDING
        case JobEvent.EXPIRED:
            job.Status = JobStatus.EXPIRED
        case _:
            job.Status = JobStatus.IN_PROGRESS
    job.save()
    events = Event.select(Event).where(Event.Job == job)
    response = job.to_response(events=[e.to_response() for e in events])
    return JSONResponse(content=response.model_dump())


@router.post("/api/artworks", tags=["api"])
def create_upload_file(
    request: Request,
    file: bytes = File(),
    category: str = Form(),
    botyo_id: str = Form(),
):
    raise HTTPException(404)
    # uploaded_path = TempPath(uuid4().hex)
    # uploaded_path.write_bytes(file)
    # with Database.db.atomic():
    #     obj = Artwork(
    #         Category=Category(category.lower()),
    #         Image=uploaded_path.as_posix(),
    #         botyo_id=botyo_id
    #     )
    #     obj.save()
    #     # colors = DominantColors(uploaded_path).colors
    #     # Artcolor.bulk_create([
    #     #     Artcolor(
    #     #         Color=rgb_to_int(color),
    #     #         Artwork=obj,
    #     #         weight=2 ** (5 - idx)
    #     #     )
    #     #     for idx, color in enumerate(colors)
    #     # ])
    #     # logging.debug(obj)
    #     # Scheduler.add_job(
    #     #     generate_palette,
    #     #     name="generate_palette",
    #     #     trigger='date',
    #     #     replace_existing=True,
    #     #     run_date=datetime.now(tz=timezone.utc) + timedelta(minutes=2)
    #     # )
    #     # return obj.to_dict()
