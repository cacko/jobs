from .base import DbModel
from jobs.database import Database
from jobs.database.fields import CleanTextField, EntityGroupField
from jobs.routers.models import SkillResponse


class Skill(DbModel):
    Group = EntityGroupField()
    name = CleanTextField()

    def to_response(self, **kwds):
        return SkillResponse(
            name=self.name,
            group=self.Group
        )

    class Meta:
        database = Database.db
        table_name = 'jobs_skill'
