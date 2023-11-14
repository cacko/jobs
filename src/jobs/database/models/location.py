from functools import lru_cache
import json

from jobs.database.fields import CleanCharField
from .base import DbModel
from jobs.database import Database
from jobs.routers.models import LocationResponse
from jobs.core.country import to_name


class Location(DbModel):
    country_iso = CleanCharField(max_length=2, default="UK")
    city = CleanCharField()

    @classmethod
    @lru_cache()
    def get_cities(cls):
        return [x[0] for x in cls.select(cls.city).tuples()]

    @classmethod
    def get_or_create(cls, **kwargs):
        kwargs["city"] = cls.get_similar(kwargs["city"], cls.get_cities())
        return super().get_or_create(**kwargs)

    @property
    def name(self) -> str:
        return f"{self.city} / {to_name(self.country_iso)}"

    def to_json(self):
        return json.dumps(dict(
            country_iso=self.country_iso,
            city=self.city
        ))

    def to_response(self, **kwds):
        return LocationResponse(
            country_iso=self.country_iso,
            city=self.city
        )

    class Meta:
        database = Database.db
        table_name = 'jobs_location'
        indexes = (
            (('country_iso', 'city'), True),
        )
