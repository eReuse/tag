from datetime import datetime

from boltons.urlutils import URL
from flask import current_app as app
from sqlalchemy import Column, Sequence, types
from teal.db import URL as URLType, check_range
from werkzeug.exceptions import BadRequest

from ereuse_tag.db import db


class HashedIdFieldTag(types.TypeDecorator):
    """
    A field that represents a BigInteger in the database and a
    hashedID representation of it in python.
    """
    impl = types.BigInteger

    def process_bind_param(self, value: str, dialect) -> int:
        provider_id, hash = value.split('-')
        assert provider_id == app.config['TAG_PROVIDER_ID'], \
            'The tag does not belong to this provider ID'
        return app.resources['Tag'].hashids.decode(hash)[0]

    def process_result_value(self, value, dialect):
        return '{}-{}'.format(app.config['TAG_PROVIDER_ID'],
                              app.resources['Tag'].hashids.encode(value))


class Tag(db.Model):
    id = Column(HashedIdFieldTag,
                Sequence('tag_id'),
                check_range('id', 1, 10 ** 12),  # Imposed by QR size
                primary_key=True)
    devicehub = Column(URLType)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def remote_tag(self) -> URL:
        """
        The URL of the linked tag.

        :raise NoRemoteTag: The tag has not been set to a Devicehub.
        :return URL: This returns something like ``https://foo.bar/tags/XYZ``.
        """
        if not self.devicehub:
            raise NoRemoteTag()
        url = URL(self.devicehub)
        url.path_parts += 'tags', self.id
        return url

    def __repr__(self) -> str:
        return '<Tag {0.id} device={0.device_id}>'.format(self)


class NoRemoteTag(BadRequest):
    description = 'This tag has not been assigned to a Devicehub.'
