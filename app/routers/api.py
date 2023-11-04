from functools import reduce
import logging
from math import floor
from typing import Optional
from uuid import uuid4
from fastapi import APIRouter, HTTPException, Request, Form, File
from app.database.database import Database
from app.database.models import (
    Company,
    Location,
    Position,
    Job,
    Event
)
from fastapi.responses import JSONResponse
from corestring import split_with_quotes
from corefile import TempPath
from peewee import fn
from datetime import datetime, timedelta, timezone


router = APIRouter()


def get_list_response(
    page: int = 1,
    limit: int = 20,
    last_modified: Optional[float] = None
):
    results = []
    filters = [True]
    order_by = []

    base_query = Job.select(Job)
    query = base_query.where(*filters)

    results = [dict(
        position=job.Position.name,
        company=job.Company.name,
        id=job.slug,
        last_modified=datetime.timestamp(job.last_modified),
        cv=job.CV.name,
        deleted=job.deleted,
        status=job.Status,
        country=job.Location.country_iso,
        city=job.Location.city,
        onsite=job.OnSiteRemote,
        source=job.Source
    ) for job in query.paginate(page, limit)]
    return JSONResponse(content=results)


@router.get("/api/jobs", tags=["api"])
def list_jobs(
    page: int = 1,
    limit: int = 20,
    last_modified: Optional[float] = None
):
    return get_list_response(
        page=page,
        limit=limit,
        last_modified=last_modified
    )


@router.get("/api/job/{slug}", tags=["api"])
def get_job(slug: str):
    try:
        job = Job.select(Job).where(Job.slug == slug).get()
        assert job
        events = Event.select(Event).where(Event.Job == job)
        return dict(
            position=job.Position.name,
            company=job.Company.name,
            id=job.slug,
            last_modified=datetime.timestamp(job.last_modified),
            cv=job.CV.name,
            deleted=job.deleted,
            status=job.Status,
            country=job.Location.country_iso,
            city=job.Location.city,
            onsite=job.OnSiteRemote,
            source=job.Source,
            events=list(events.dicts())
        )
    except AssertionError:
        raise HTTPException(404)


@router.post("/api/artworks", tags=["api"])
def create_upload_file(
    request: Request,
    file: bytes = File(),
    category: str = Form(),
    botyo_id: str = Form()

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
