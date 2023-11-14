from .base import DbModel
from peewee import (
    TextField,
    ForeignKeyField,
    DateTimeField
)
from app.database import Database
from app.database.fields import JobEventField
from app.routers.models import JobEventResponse
from datetime import datetime
from .job import Job


class Event(DbModel):

    Job = ForeignKeyField(Job)
    Event = JobEventField()
    description = TextField()
    timestamp = DateTimeField(default=datetime.now)

    def to_response(self, **kwds):
        return JobEventResponse(
            event=self.Event,
            description=self.description.strip(),
            timestamp=self.timestamp
        )

    class Meta:
        database = Database.db
        table_name = 'jobs_event'
        order_by = ["-timestamp"]
