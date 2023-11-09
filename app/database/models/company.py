from functools import lru_cache

from app.routers.models import CompanyResponse
from .base import DbModel
from peewee import (
    CharField
)
from app.database import Database


class Company(DbModel):
    name = CharField(unique=True)
    url = CharField(null=True)

    @classmethod
    @lru_cache()
    def get_names(cls):
        return [x[0] for x in cls.select(cls.name).tuples()]

    @classmethod
    def get_or_create(cls, **kwargs):
        kwargs["name"] = cls.get_similar(kwargs["name"], cls.get_names())
        return super().get_or_create(**kwargs)

    def to_response(self, **kwds):
        return CompanyResponse(**self.to_dict())

    class Meta:
        database = Database.db
        table_name = 'jobs_company'
        order_by = ["name"]
