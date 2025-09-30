from .base import DbModel
from jobs.database import Database
from jobs.database.fields import CleanCharField
from peewee import IntegrityError

class User(DbModel):
    email = CleanCharField(unique=True)
    uuid = CleanCharField(unique=True)
    name = CleanCharField(null=True)
    picture = CleanCharField(null=True)

    @classmethod
    def get_or_create(cls, **kwargs) -> tuple["User", bool]:
        defaults = kwargs.pop("defaults", {})
        query = cls.select()
        query = query.where((User.uuid == kwargs.get("uuid")) | (User.email == kwargs.get("email")))

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

    class Meta:
        database = Database.db
        table_name = "jobs_users"
