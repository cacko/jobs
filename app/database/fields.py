from peewee import CharField, TextField
from app.core.s3 import S3
from uuid import uuid4
from pathlib import Path
from corefile import TempPath
from PIL import Image
from app.routers.models import ImageReponse
from app.config import app_config
from .enums import LocationType, Source, JobEvent, JobStatus

CDN_ROOT = (
    f"https://{app_config.aws.cloudfront_host}"
    f"/{app_config.aws.media_location}"
)


class CleanCharField(CharField):

    def db_value(self, value):
        try:
            assert value
            return super().db_value(value).strip()
        except AssertionError:
            return super().db_value(value)

    def python_value(self, value):
        try:
            assert value
            return super().python_value(value).strip()
        except AssertionError:
            return super().python_value(value)


class CleanTextField(TextField):

    def db_value(self, value):
        try:
            assert value
            return super().db_value(value).strip()
        except AssertionError:
            return super().db_value(value)

    def python_value(self, value):
        try:
            assert value
            return super().python_value(value).strip()
        except AssertionError:
            return super().python_value(value)


class LocationTypeField(CharField):

    def db_value(self, value: LocationType):
        return value.value

    def python_value(self, value):
        return LocationType(value)


class SourceField(CharField):

    def db_value(self, value: Source):
        return value.value

    def python_value(self, value):
        return Source(value)


class JobStatusField(CharField):

    def db_value(self, value: JobStatus):
        return value.value

    def python_value(self, value):
        return JobStatus(value)


class JobEventField(CharField):

    def db_value(self, value: JobEvent):
        return value.value

    def python_value(self, value):
        return JobEvent(value)


class ImageFieldMeta(type):

    def raw_src(cls, image_path: Path) -> str:
        stem = image_path.stem
        return f"{CDN_ROOT}/{stem}.png.png"

    def webp_src(cls, image_path: Path) -> str:
        stem = image_path.stem
        return f"{CDN_ROOT}/{stem}.webp"

    def thumb_src(cls, image_path: Path) -> str:
        stem = image_path.stem
        return f"{CDN_ROOT}/{stem}.thumbnail.webp"

    def to_response(cls, image: str):
        pth = Path(image)
        return ImageReponse(
            thumb_src=cls.thumb_src(pth),
            webp_src=cls.webp_src(pth),
            raw_src=cls.raw_src(pth)
        )


class ImageField(CharField, metaclass=ImageFieldMeta):

    def db_value(self, value: str):
        image_path = Path(value)
        assert image_path.exists()
        stem = uuid4().hex

        raw_fname = f"{stem}.png.png"
        S3.upload(image_path, raw_fname)

        img = Image.open(image_path.as_posix())

        webp_fname = f"{stem}.webp"
        webp_path = TempPath(webp_fname)
        img.save(webp_path.as_posix())
        S3.upload(webp_path, webp_fname)

        img.thumbnail((300, 300))
        thumb_fname = f"{stem}.thumbnail.webp"
        thumb_path = TempPath(thumb_fname)
        img.save(thumb_path.as_posix())
        S3.upload(thumb_path, thumb_fname)

        return webp_fname

    def python_value(self, value):
        return value
