from .database import Database
from .models import (
    Company,
    Location,
    CV,
    Job,
    Event,
    Position,
    Skill,
    JobSkill
)


def create_tables(drop=False):
    tables = [
        Company,
        Location,
        CV,
        Job,
        Event,
        Position,
        Skill,
        JobSkill
    ]
    if drop:
        Database.db.drop_tables(tables)
    Database.db.create_tables(tables)
