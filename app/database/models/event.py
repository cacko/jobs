from .base import DbModel
from peewee import (
    CharField,
    ForeignKeyField,
)
from app.database import Database
from app.database.fields import JobEventField
from .job import Job


class Event(DbModel):

    Job = ForeignKeyField(Job)
    Event = JobEventField()
    description = CharField()

    class Meta:
        database = Database.db
        table_name = 'jobs_event'
        order_by = ["name"]
