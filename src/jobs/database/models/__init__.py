from .company import Company
from .cv import CV
from .location import Location
from .event import Event
from .job import Job, JobSkill
from .position import Position
from .skill import Skill
from .cover_letter import CoverLetter
from .user import User

from playhouse.signals import post_save
from jobs.firebase.db import UpdatesDb


@post_save(sender=Job)
def on_save_handler(model_class, instance, created):
    logging.info(f"Saved {model_class.__name__} instance: {instance}")
    if hasattr(instance, 'useremail') and hasattr(instance, 'last_modified'):
        UpdatesDb().updates(instance.useremail, instance.last_modified)

__all__ = [
    "Company",
    "CV",
    "Location",
    "Event",
    "Job",
    "Position",
    "Skill",
    "JobSkill",
    "CoverLetter",
    "User"
]