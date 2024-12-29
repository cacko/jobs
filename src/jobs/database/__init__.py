from .database import Database
from .models import (
    Company,
    Location,
    CV,
    Job,
    Event,
    Position,
    Skill,
    JobSkill,
    CoverLetter
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
        JobSkill,
        CoverLetter
    ]
    if drop:
        Database.db.drop_tables(tables)
    Database.db.create_tables(tables)
