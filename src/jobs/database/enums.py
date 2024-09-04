from enum import StrEnum


CV_PATH = "/Volumes/Devo/Users/jago/Documents/AleksandarSpasov"


class Choices(object):

    @classmethod
    def values(cls):
        return [m.value for m in cls.__members__.values()]

    @classmethod
    def keys(cls):
        return [m.lower() for m in cls.__members__.keys()]

    @classmethod
    def members(cls):
        return cls.__members__.values()


class Source(Choices, StrEnum):
    LINKEDIN = "linkedin"
    DWP = "dwp"
    DIRECT = "direct"

    @classmethod
    def values(cls):
        return [member.value for member in cls.__members__.values()]

    @classmethod
    def to_categories(cls, values: list[str]) -> list["Source"]:
        return [cls(x.lower()) for x in values if x.lower() in cls.values()]


class LocationType(Choices, StrEnum):
    ONSITE = "onsite"
    HYBRID = "hybrid"
    REMOTE = "remote"


class JobStatus(Choices, StrEnum):
    PENDING = "pending"
    REJECTED = "rejected"
    EXPIRED = "expired"
    IN_PROGRESS = "in_progress"


class JobEvent(Choices, StrEnum):
    APPLIED = "applied"
    INTERVIEW = "interview"
    TEST = "test"
    RESPONSE = "response"
    REJECT = "reject"
    EXPIRED = "expired"


class EntityGroup(Choices, StrEnum):
    TECHNICAL = "TECHNICAL"
    BUSINESS = "BUS"
    TECHNOLOGY = "TECHNOLOGY"
    SOFT = "SOFT"
