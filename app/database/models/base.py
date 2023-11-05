import datetime
import json
from typing import Any
from peewee import Model, DoesNotExist
from playhouse.shortcuts import model_to_dict
from humanfriendly.tables import format_robust_table
from fuzzelinho import extract
from json import JSONEncoder


class PeeEncoder(JSONEncoder):

    def default(self, o: Any) -> Any:
        match o:
            case datetime.datetime():
                return datetime.datetime.timestamp(0)
        return super().default(o)


def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)


_default.default = JSONEncoder().default
JSONEncoder.default = _default


class DbModel(Model):
    @classmethod
    def fetch(cls, *query, **filters):
        try:
            return cls.get(*query, **filters)
        except DoesNotExist:
            return None

    @classmethod
    def get_similar(cls, query, values):
        try:
            assert values
            result = extract(query, values)
            assert result
            return result
        except AssertionError:
            return query

    def to_dict(self):
        return model_to_dict(self)
    
    def to_json(self):
        return json.dumps(self.to_dict())

    def to_table(self):
        data = self.to_dict()
        columns = list(data.keys())
        values = list(data.values())
        return format_robust_table(
            [values],
            column_names=columns
        )
