from pydantic import BaseModel
from enum import StrEnum

from jobs.database.enums import EntityGroup


class ENDPOINT(StrEnum):
    SKILLS = "text/skills"


class Token(BaseModel):
    entity_group: EntityGroup
    score: float
    word: str
