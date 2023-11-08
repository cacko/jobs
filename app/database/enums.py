from enum import StrEnum


class Source(StrEnum):
    LINKEDIN = "linkedin"
    DIRECT = "direct"

    @classmethod
    def values(cls):
        return [member.value for member in cls.__members__.values()]

    @classmethod
    def to_categories(cls, values: list[str]) -> list['Source']:
        return [cls(x.lower()) for x in values if x.lower() in cls.values()]


class LocationType(StrEnum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class JobStatus(StrEnum):
    PENDING = "pending"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"


class JobEvent(StrEnum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    RESPONSE = "response"
