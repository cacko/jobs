from typing import Optional

from yaml import Token

from jobs.database.models.skill import Skill
from jobs.firebase.db import UpdatesDb
from .base import DbModel, default_timestamp
from .company import Company
from .location import Location
from .position import Position
from .user import User
from .cv import CV
from .cover_letter import CoverLetter
from jobs.database import Database
from jobs.database.fields import (
    JobStatusField,
    LocationTypeField,
    SourceField
)
from peewee import (
    CharField,
    ForeignKeyField,
    BooleanField,
    IntegrityError,
    ManyToManyField
)
from playhouse.postgres_ext import DateTimeTZField
from jobs.config import app_config
from slugify import slugify
from jobs.routers.models import JobResponse

class Job(DbModel):
    Source = SourceField()
    Company = ForeignKeyField(Company)
    OnSiteRemote = LocationTypeField()
    Location = ForeignKeyField(Location, null=True)
    CV = ForeignKeyField(CV)
    Status = JobStatusField()
    Position = ForeignKeyField(Position)
    skills = ManyToManyField(Skill, backref='jobs')
    url = CharField()
    last_modified = DateTimeTZField(default=default_timestamp)
    slug = CharField()
    deleted = BooleanField(default=False)
    CoverLetter = ForeignKeyField(CoverLetter, null=True)
    User = ForeignKeyField(User)

    @classmethod
    def get_slug(cls, **kwds) -> Optional[str]:
        company = kwds.get("Company")
        assert company
        position = kwds.get("Position")
        assert position
        url = kwds.get("url")
        assert url
        return slugify(f"{company.name} {position.name} {url}")

    @classmethod
    def get_or_create(cls, **kwargs) -> tuple['Job', bool]:
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
        self.last_modified = default_timestamp()
        self.save(only=["deleted", "last_modified"])

    def save(self, *args, **kwds):
        if not self.slug:
            self.slug = self.__class__.get_slug(**dict(
                Company=self.Company,
                Position=self.Position,
                url=self.url
            ))
        if 'only' not in kwds:
            self.last_modified = default_timestamp()
        UpdatesDb().updates(self.useremail, self.last_modified)
        return super().save(*args, **kwds)
    
    @property
    def useremail(self) -> str:
        return f"{self.User.email}"
    
    @property
    def useruuid(self) -> str:
        return f"{self.User.uuid}"

    @property
    def web_uri(self) -> str:
        return f"{app_config.api.web_host}/{self.useremail}/{self.slug}"

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
            url=self.url,
            skills=[s.to_response() for s in self.skills],
            cover_letter=self.CoverLetter.to_response() if self.CoverLetter else None,
            useremail=self.useremail,
            useruuid=self.useruuid,
            **kwds
        )

    def add_skills(self, tokens: list[Token]):
        self.skills.clear()
        new_skills = [Skill.get_or_create(
            Group=token.entity_group,
            name=token.word
        )[0] for token in tokens]
        self.skills.add(new_skills)
        self.last_modified = default_timestamp()
        self.save(only=["deleted", "last_modified"])

    class Meta:
        database = Database.db
        table_name = 'jobs_job'
        order_by = ["-last_modified"]
        indexes = (
            (('User', 'last_modified'), False),  # Note the trailing comma!
            (('User', 'slug'), True),
        )


JobSkill = Job.skills.get_through_model()

