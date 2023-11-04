from .base import DbModel
from peewee import (
    CharField
)
from app.database import Database
from functools import lru_cache


class Position(DbModel):
    name = CharField(unique=True)

    @classmethod
    @lru_cache()
    def get_names(cls):
        return [x[0] for x in cls.select(cls.name).tuples()]

    @classmethod
    def get_or_create(cls, **kwargs):
        kwargs["name"] = cls.get_similar(kwargs["name"], cls.get_names())
        return super().get_or_create(**kwargs)

    class Meta:
        database = Database.db
        table_name = 'jobs_position'
        order_by = ["name"]
