import teal.db
from boltons.urlutils import URL
from flask import current_app as app
from sqlalchemy import Column, Sequence, types
from sqlalchemy.ext.declarative import declared_attr
from teal.db import URL as URLType, check_range
from teal.resource import url_for_resource
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
    devicehub = Column(URLType, comment='URL with the database')
    type = Column(db.Unicode(), nullable=False, index=True)
    updated = db.Column(db.TIMESTAMP(timezone=True),
                        server_default=db.text('CURRENT_TIMESTAMP'),
                        nullable=False)
    created = db.Column(db.TIMESTAMP(timezone=True),
                        server_default=db.text('CURRENT_TIMESTAMP'),
                        nullable=False)

    @property
    def url(self):
        return url_for_resource(self, self.id)

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

    @declared_attr
    def __mapper_args__(cls):
        """
        Defines inheritance.

        From `the guide <http://docs.sqlalchemy.org/en/latest/orm/
        extensions/declarative/api.html
        #sqlalchemy.ext.declarative.declared_attr>`_
        """
        args = {teal.db.POLYMORPHIC_ID: cls.t}
        if cls.t == 'Tag':
            args[teal.db.POLYMORPHIC_ON] = cls.type
        return args

    def __repr__(self) -> str:
        return '<Tag {0.id} device={0.device_id}>'.format(self)


class ETag(Tag):
    pass


class NoRemoteTag(BadRequest):
    description = 'This tag has not been assigned to a Devicehub.'


class Link(db.Model):
    """A Link to an URL.

    Stores URLs and provides a hashed ID back.
    """
    # todo develop
    id = Column(HashedIdFieldTag, Sequence('link_id'), primary_key=True)
    url = Column(URLType, nullable=False, unique=True)
    updated = db.Column(db.TIMESTAMP(timezone=True),
                        server_default=db.text('CURRENT_TIMESTAMP'),
                        nullable=False)
    created = db.Column(db.TIMESTAMP(timezone=True),
                        server_default=db.text('CURRENT_TIMESTAMP'),
                        nullable=False)
