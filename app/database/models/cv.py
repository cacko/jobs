from typing import Optional
from app.database import Database
from .base import DbModel
from app.database.fields import (
    ImageField,
)
from peewee import (
    CharField,
    DateTimeField,
    BlobField, IntegrityError
)
from app.config import app_config
from pathlib import Path
from slugify import slugify
from hashlib import sha1
from playhouse.shortcuts import model_to_dict
from corefile import TempPath
from corefile.filepath import file_hash
from datetime import datetime, timezone
from app.core.pdf import to_pil

CDN_ROOT = (
    f"https://{app_config.aws.cloudfront_host}"
    f"/{app_config.aws.media_location}"
)


class CV(DbModel):
    slug = CharField(unique=True)
    name = CharField()
    data = BlobField()
    Image = ImageField()
    added = DateTimeField(default=datetime.now)

    def to_dict(self):
        data = model_to_dict(self)
        del data["data"]
        return {
            **data,
            **dict(
                thumb_src=self.thumb_src,
                webp_src=self.webp_src,
                raw_src=self.raw_src
            )
        }

    @classmethod
    def from_path(cls, cv_path: Path):
        assert cv_path.exists()
        fhash = file_hash(cv_path)
        tmp = TempPath(f"{cv_path.stem}-{fhash}.png")
        img = to_pil(cv_path)
        img.save(tmp.as_posix())
        cv, _ = cls.get_or_create(
            name=cv_path.stem,
            data=cv_path.read_bytes(),
            Image=tmp.as_posix(),
            added=datetime.now(tz=timezone.utc)
        )
        return cv

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

    @property
    def raw_src(self) -> str:
        stem = (Path(self.Image)).stem
        return f"{CDN_ROOT}/{stem}.png.png"

    @property
    def webp_src(self) -> str:
        stem = (Path(self.Image)).stem
        return f"{CDN_ROOT}/{stem}.webp"

    @property
    def thumb_src(self) -> str:
        stem = (Path(self.Image)).stem
        return f"{CDN_ROOT}/{stem}.thumbnail.webp"

    class Meta:
        database = Database.db
        table_name = 'jobs_cv'
        order_by = ["name"]
