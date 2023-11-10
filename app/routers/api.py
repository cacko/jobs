import logging
from typing import Optional
from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Form,
    File,
    Depends
)
from app.database.enums import JobEvent
from app.database.models import (
    Job,
    Event
)
from app.database.export import to_xlsx
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
from .auth import check_auth

router = APIRouter()


def get_list_response(
    page: int = 1,
    limit: int = 20,
    last_modified: Optional[float] = None
):
    results = []
    filters = [Event.Event == JobEvent.APPLIED]
    # order_by = []

    base_query = Event.select().join_from(Event, Job)
    query = base_query.where(*filters)

    results = [event.Job.to_response(events=[event.to_response()]).model_dump()
               for event in query.paginate(page, limit)]
    logging.debug(results)
    return JSONResponse(content=results)


@router.get("/api/jobs", tags=["api"])
def list_jobs(
    page: int = 1,
    limit: int = 20,
    last_modified: Optional[datetime] = None,
    auth_user=Depends(check_auth)
):
    return get_list_response(
        page=page,
        limit=limit,
        last_modified=last_modified
    )


@router.get("/api/job/{slug}", tags=["api"])
def get_job(
    slug: str,
    auth_user=Depends(check_auth)
):
    try:
        job: Job = Job.select(Job).where(Job.slug == slug).get()
        assert job
        events = Event.select(Event).where(Event.Job == job)
        response = job.to_response(events=[e.to_response() for e in events])
        return JSONResponse(content=response.model_dump())
    except AssertionError:
        raise HTTPException(404)


@router.get("/api/jobs.xlsx", tags=["api"])
def xlsx_export():
    xlsx_path = to_xlsx()
    assert xlsx_path.exists()
    return FileResponse(
        path=xlsx_path.as_posix(),
        filename=xlsx_path.name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


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
