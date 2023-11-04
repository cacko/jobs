from .base import DbModel
from peewee import (
    CharField
)
from app.database import Database


class Position(DbModel):
    name = CharField(unique=True)

    class Meta:
        database = Database.db
        table_name = 'jobs_position'
        order_by = ["name"]
