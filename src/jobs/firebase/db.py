from datetime import datetime
from jobs.firebase.service_account import db

class UpdatesDb(object):

    @property
    def root_ref(self):
        return db.reference(f"updates")

    def updates(self, useruuid: str, timestamp: datetime):
        user_ref = self.root_ref.child(useruuid)
        return user_ref.set(timestamp.isoformat())
