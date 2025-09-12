from datetime import datetime
from jobs.firebase.service_account import db
from hashlib import md5


class UpdatesDb(object):

    @property
    def root_ref(self):
        return db.reference(f"updates")

    def updates(self, useremail: str, timestamp: datetime):
        user_ref = self.root_ref.child(md5(useremail.encode()).hexdigest())
        return user_ref.set(timestamp.isoformat())
