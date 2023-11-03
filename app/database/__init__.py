from .database import Database
from .models import Company, Location, CV, Job, Event


def create_tables():
    Database.db.create_tables([
        Company,
        Location,
        CV,
        Job,
        Event
    ])

