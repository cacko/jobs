import logging
import typer
from jobs.cli.prompts.events import EventInput, EventIdInput
from jobs.cli.prompts.job import JobInput
from jobs.cli.prompts.jobs import ApplyInput
from jobs.core.country import to_iso
from jobs.database.enums import JobEvent, JobStatus
from jobs.database.models.company import Company
from jobs.database.models.cover_letter import CoverLetter
from jobs.database.models.cv import CV
from jobs.database.models.event import Event
from jobs.database.models.job import Job
from jobs.database.models.location import Location
from jobs.database.models.position import Position
from jobs.database.models.skill import Skill
from jobs.database.models.user import User
from jobs.masha.skills import Skills
from datetime import datetime, timezone, timedelta


def cmd_apply(input: ApplyInput):
    location_obj, _ = Location.get_or_create(
        country_iso=to_iso(input.country),
        city=input.city
    )
    position_obj, _ = Position.get_or_create(name=input.position)
    cv_obj = CV.from_path(input.cv)
    cover_letter_obj = CoverLetter.from_path(input.cover_letter)
    company_obj, _ = Company.get_or_create(name=input.company)
    user_obj = User.get(User.email == "alex@cacko.net")

    job, created = Job.get_or_create(
        Source=input.source,
        Company=company_obj,
        OnSiteRemote=input.site,
        Location=location_obj,
        CV=cv_obj,
        Status=input.status,
        url=input.url,
        Position=position_obj,
        CoverLetter=cover_letter_obj,
        User=user_obj
    )

    logging.debug(f"Created: {created}")
    logging.info(f"\n{job.to_table()}")

    event, created = Event.get_or_create(
        Job=job,
        Event=JobEvent.APPLIED,
        description=input.note
    )

    logging.debug(f"Created: {created}")
    logging.info(f"\n{event.to_table()}")

    skills = Skills(input.note).result
    Skill.print(skills)
    job.add_skills(tokens=skills)


def cmd_event(input: EventInput):
    job: Job = Job.get(Job.slug == input.job_id)
    event, created = Event.get_or_create(
        Job=job,
        Event=input.event,
        description=input.description
    )
    logging.info(f"{event} created={created}")
    match input.event:
        case JobEvent.REJECT:
            job.Status = JobStatus.REJECTED
        case JobEvent.APPLIED:
            job.Status = JobStatus.PENDING
        case _:
            job.Status = JobStatus.IN_PROGRESS
    job.save()
    logging.debug(f"Changaing job status to {job.Status}")

def cmd_delete_event(input: EventIdInput):
    event: Event = Event.get(Event.id == input.event_id)
    print(event)
    job = event.Job
    event.delete_instance()
    print(job)
    last_event = Event.select().where(Event.Job == job).order_by(Event.timestamp.desc()).first()
    match last_event.Event if last_event else None: 
        case JobEvent.REJECT:
            job.Status = JobStatus.REJECTED
        case JobEvent.APPLIED:
            job.Status = JobStatus.PENDING
        case _:
            job.Status = JobStatus.IN_PROGRESS
    job.save()
    logging.info(f"Deleted event: {event}")

def cmd_tokens(input: JobInput):
    job: Job = Job.get(Job.slug == input.job_id)
    apply: Event = Event.get(Event.Job == job, Event.Event == JobEvent.APPLIED)
    skills = Skills(apply.description).result
    Skill.print(skills)
    if typer.confirm("update skills?"):
        job.add_skills(tokens=skills)

def cmd_expire(input: JobInput):
    job: Job = Job.get(Job.slug == input.job_id)
    event, created = Event.get_or_create(
        Job=job,
        Event=JobEvent.EXPIRED,
        description="Lack of response"
    )
    logging.info(f"{event} created={created}")
    job.Status = JobStatus.EXPIRED
    job.save()
    
def cmd_auto_expire():
    threshold_delta = timedelta(weeks=8)
    threshold = datetime.now(tz=timezone.utc) - threshold_delta
    query = Job.select().where(*[
        Job.Status == JobStatus.PENDING,
        Job.last_modified < threshold
    ])
    for job in query:
        Event.get_or_create(
            Job=job,
            Event=JobEvent.EXPIRED,
            description="Lack of response"
        )
        logging.info(f"{job.job_name} expired")
        job.Status = JobStatus.EXPIRED
        job.save()

