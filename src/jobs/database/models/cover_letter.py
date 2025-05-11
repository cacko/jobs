from typing import Optional
from jobs.database import Database
from .base import DbModel, default_timestamp
from jobs.database.fields import (
    ImageField,
)
from peewee import (
    CharField,
    DateTimeField,
    BlobField, IntegrityError
)
from pathlib import Path
from slugify import slugify
from hashlib import sha1
from playhouse.shortcuts import model_to_dict
from corefile import TempPath
from corefile.filepath import file_hash
from datetime import datetime, timezone
from jobs.core.pdf import to_pil
from jobs.routers.models import CoverLetterResponse


class CoverLetter(DbModel):
    slug = CharField(unique=True)
    name = CharField()
    data = BlobField()
    Image = ImageField()
    added = DateTimeField(default=default_timestamp, utc=True)

    def to_dict(self):
        data = model_to_dict(self)
        del data["data"]
        return data

    def to_response(self, **kwds):
        data = self.to_dict()
        data.setdefault("image", ImageField.to_response(self.Image))
        return CoverLetterResponse(**data)

    @classmethod
    def from_path(cls, cl_path: Path):
        try:
            assert cl_path.exists()
            assert cl_path.is_file()
            assert cl_path.suffix.lower() == ".pdf"
            fhash = file_hash(cl_path)
            tmp = TempPath(f"{cl_path.stem}-{fhash}.png")
            img = to_pil(cl_path)
            img.save(tmp.as_posix())
            cv, _ = cls.get_or_create(
                name=cl_path.stem,
                data=cl_path.read_bytes(),
                Image=tmp.as_posix(),
                added=datetime.now(tz=timezone.utc).replace(tzinfo=None)
            )
            return cv
        except AssertionError:
            return None

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

    @classmethod
    def get_slug(cls, **kwds) -> Optional[str]:
        try:
            data = kwds.get("data")
            assert data
            name = kwds.get("name")
            assert name
            hash = sha1(data).hexdigest()
            return slugify(f"{name} {hash}")
        except AssertionError:
            return None

    def save(self, *args, **kwds):
        self.slug = self.__class__.get_slug(**model_to_dict(self))
        return super().save(*args, **kwds)

    class Meta:
        database = Database.db
        table_name = 'jobs_cover_letter'
        order_by = ["name"]
