from typing import Optional
from .base import DbModel
from .company import Company
from .location import Location
from .position import Position
from .cv import CV
from app.database import Database
from app.database.fields import (
    JobStatusField,
    LocationTypeField,
    SourceField
)
from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    BooleanField,
    IntegrityError
)
from app.config import app_config
import datetime
from slugify import slugify
from app.routers.models import JobResponse


class Job(DbModel):
    Source = SourceField()
    Company = ForeignKeyField(Company)
    OnSiteRemote = LocationTypeField()
    Location = ForeignKeyField(Location, null=True)
    CV = ForeignKeyField(CV)
    Status = JobStatusField()
    Position = ForeignKeyField(Position)
    ad_url = CharField()
    last_modified = DateTimeField(default=datetime.datetime.now)
    slug = CharField(unique=True)
    deleted = BooleanField(default=False)

    @classmethod
    def get_slug(cls, **kwds) -> Optional[str]:
        company = kwds.get("Company")
        assert company
        position = kwds.get("Position")
        assert position
        ad_url = kwds.get("ad_url")
        assert ad_url
        return slugify(f"{company.name} {position.name} {ad_url}")

    @classmethod
    def get_or_create(cls, **kwargs):
        defaults = kwargs.pop('defaults', {})
        query = cls.select()
        slug = cls.get_slug(**kwargs)
        query = query.where(cls.slug == slug)

        try:
            return query.get(), False
        except cls.DoesNotExist:
            try:
                if defaults:
                    kwargs.update(defaults)
                with cls._meta.database.atomic():
                    return cls.create(**kwargs), True
            except IntegrityError as exc:
                try:
                    return query.get(), False
                except cls.DoesNotExist:
                    raise exc

    def delete_instance(self, recursive=False, delete_nullable=False):
        self.deleted = True
        self.last_modified = datetime.datetime.now()
        self.save(only=["deleted", "last_modified"])

    def save(self, *args, **kwds):
        if not self.slug:
            self.slug = self.__class__.get_slug(**dict(
                Company=self.Company,
                Position=self.Position,
                ad_url=self.ad_url
            ))
        self.last_modified = datetime.datetime.now()
        return super().save(*args, **kwds)

    @property
    def web_uri(self) -> str:
        return f"{app_config.api.web_host}/v/{self.slug}"

    @property
    def job_name(self) -> str:
        return f"{self.Company.name}: {self.Position.name}"

    def to_response(self, **kwds):
        return JobResponse(
            position=self.Position.name,
            company=self.Company.to_response(),
            id=self.slug,
            last_modified=self.last_modified,
            cv=self.CV.to_response(),
            deleted=self.deleted,
            status=self.Status,
            location=self.Location.to_response(),
            onsite=self.OnSiteRemote,
            source=self.Source,
            url=self.ad_url,
            **kwds
        )

    class Meta:
        database = Database.db
        table_name = 'jobs_job'
        order_by = ["-last_modified"]
