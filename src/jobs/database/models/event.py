from .base import DbModel, default_timestamp
from peewee import (
    ForeignKeyField,
    DateTimeField
)
from jobs.database import Database
from jobs.database.fields import CleanTextField, JobEventField
from jobs.routers.models import JobEventResponse
from .job import Job


class Event(DbModel):

    Job = ForeignKeyField(Job)
    Event = JobEventField()
    description = CleanTextField()
    timestamp = DateTimeField(default=default_timestamp)
    
    @classmethod
    def get_or_create(cls, **kwargs) -> tuple['Event', bool]:
        return super().get_or_create(**kwargs)

    def to_response(self, **kwds):
        return JobEventResponse(
            event=self.Event,
            description=self.description,
            timestamp=self.timestamp
        )

    class Meta:
        database = Database.db
        table_name = 'jobs_event'
        order_by = ["-timestamp"]
