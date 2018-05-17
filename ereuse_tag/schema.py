from marshmallow.fields import Date, Integer
from teal.marshmallow import URL
from teal.resource import Schema


class Tag(Schema):
    id = Integer(description='The ID of the tag.', dump_only=True)
    same_as = URL(description='The URL pointing at the device.')
    created = Date('iso', dump_only=True)
    updated = Date('iso', dump_only=True)
