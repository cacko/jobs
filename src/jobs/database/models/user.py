from itertools import groupby
from yaml import Token
from .base import DbModel
from jobs.database import Database
from jobs.database.fields import CleanCharField
from jobs.routers.models import SkillResponse
from humanfriendly.tables import format_robust_table


class User(DbModel):
    email = CleanCharField(unique=True)
    uuid = CleanCharField(unique=True)
    name=CleanCharField(null=True)

    class Meta:
        database = Database.db
        table_name = 'jobs_users'
