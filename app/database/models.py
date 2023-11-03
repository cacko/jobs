from peewee import Model, DoesNotExist
from .database import Database
from .fields import (
    ImageField,
    JobEventField,
    JobStatusField,
    LocationTypeField,
    SourceField
)
from playhouse.shortcuts import model_to_dict
from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    BooleanField,
    BlobField
)
from app.config import app_config
from pathlib import Path
from stringcase import spinalcase
import datetime

CDN_ROOT = (
    f"https://{app_config.aws.cloudfront_host}"
    f"/{app_config.aws.media_location}"
)


class DbModel(Model):
    @classmethod
    def fetch(cls, *query, **filters):
        try:
            return cls.get(*query, **filters)
        except DoesNotExist:
            return None

    def to_dict(self):
        return model_to_dict(self)


class Company(DbModel):
    name = CharField()

    class Meta:
        database = Database.db
        table_name = 'jobs_company'
        order_by = ["name"]


class Location(DbModel):
    Type = LocationTypeField()
    country_iso = CharField(max_length=2, default="UK", null=True)
    city = CharField(null=True)
    address = CharField(null=True)

    class Meta:
        database = Database.db
        table_name = 'jobs_location'


class CV(DbModel):

    name = CharField()
    data = BlobField()
    Image = ImageField()

    @property
    def raw_src(self) -> str:
        stem = (Path(self.Image)).stem
        return f"{CDN_ROOT}/{stem}.png.png"

    @property
    def webp_src(self) -> str:
        stem = (Path(self.Image)).stem
        return f"{CDN_ROOT}/{stem}.webp"

    @property
    def thumb_src(self) -> str:
        stem = (Path(self.Image)).stem
        return f"{CDN_ROOT}/{stem}.thumbnail.webp"

    class Meta:
        database = Database.db
        table_name = 'jobs_cv'
        order_by = ["name"]


class Job(DbModel):
    Source = SourceField()
    Company = ForeignKeyField(Company)
    Location = ForeignKeyField(Location)
    CV = ForeignKeyField(CV)
    Status = JobStatusField()
    ad_url = CharField()
    last_modified = DateTimeField(default=datetime.datetime.now)
    slug = CharField()
    deleted = BooleanField(default=False)

    def delete_instance(self, recursive=False, delete_nullable=False):
        self.deleted = True
        self.last_modified = datetime.datetime.now()
        self.save(only=["deleted", "last_modified"])

    def save(self, *args, **kwds):
        self.slug = spinalcase(self.Name)
        return super().save(*args, **kwds)

    @property
    def web_uri(self) -> str:
        return f"{app_config.api.web_host}/v/{self.slug}"

    class Meta:
        database = Database.db
        table_name = 'jobs_job'
        order_by = ["-last_modified"]


class Event(DbModel):

    Job = ForeignKeyField(Job)
    Event = JobEventField()
    description = CharField()

    class Meta:
        database = Database.db
        table_name = 'jobs_event'
        order_by = ["name"]
