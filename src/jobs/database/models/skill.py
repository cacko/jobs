from itertools import groupby
from yaml import Token
from .base import DbModel
from jobs.database import Database
from jobs.database.fields import CleanTextField, EntityGroupField
from jobs.routers.models import SkillResponse
from humanfriendly.tables import format_robust_table


class Skill(DbModel):
    Group = EntityGroupField()
    name = CleanTextField()

    def to_response(self, **kwds):
        return SkillResponse(
            name=self.name,
            group=self.Group
        )

    @classmethod
    def print(cls, tokens: list[Token]):
        skills = sorted(tokens, key=lambda s: s.entity_group)
        columns = []
        row = []
        for k, g in groupby(skills, key=lambda s: s.entity_group):
            columns.append(k)
            row.append(",".join([t.word for t in g]))
        print(format_robust_table([row], columns))

    class Meta:
        database = Database.db
        table_name = 'jobs_skill'
