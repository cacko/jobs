from .base import DbModel
from peewee import (
    CharField
)
from app.database import Database


class Company(DbModel):
    name = CharField(unique=True)

    class Meta:
        database = Database.db
        table_name = 'jobs_company'
        order_by = ["name"]
