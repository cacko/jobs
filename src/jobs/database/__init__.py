from .database import Database
from .models import Company, Location, CV, Job, Event, Position


def create_tables():
    tables = [
        Company,
        Location,
        CV,
        Job,
        Event,
        Position
    ]
    Database.db.drop_tables(tables)
    Database.db.create_tables(tables)
