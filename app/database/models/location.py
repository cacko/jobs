from .base import DbModel
from peewee import (
    CharField
)
from app.database import Database


class Location(DbModel):
    country_iso = CharField(max_length=2, default="UK")
    city = CharField()

    class Meta:
        database = Database.db
        table_name = 'jobs_location'
        indexes = (
            (('country_iso', 'city'), True),
        )
