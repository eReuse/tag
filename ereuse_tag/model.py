import teal.db
from boltons.urlutils import URL
from flask import current_app, current_app as app
from sqlalchemy import Column, Sequence
from sqlalchemy.ext.declarative import declared_attr
from teal.db import URL as URLType, check_range
from teal.resource import url_for_resource
from werkzeug.exceptions import BadRequest, UnprocessableEntity

from ereuse_tag.db import db


class Tag(db.Model):
    _id = Column('id',
                 db.BigInteger,
                 Sequence('tag_id_seq'),
                 check_range('id', 1, 10 ** 12),  # Imposed by QR size
                 primary_key=True)
    secondary = Column(db.Unicode)
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
        """The URL of the linked tag.

        :raise NoRemoteTag: The tag has not been set to a Devicehub.
        :return URL: This returns something like ``https://foo.bar/tags/XYZ``.
        """
        if not self.devicehub:
            raise NoRemoteTag()
        url = URL(self.devicehub)
        url.path_parts += 'tags', self.id
        return url

    @property
    def remote_device(self) -> URL:
        """The URL of the linked device. See :meth:`.remote_tag`."""
        tag_url = self.remote_tag
        tag_url.path_parts += 'device',
        return tag_url

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

    @property
    def id(self):
        return app.resources['Tag'].hashids.encode(self._id)

    @id.setter
    def id(self, id):
        self._id = self.decode(id)

    @classmethod
    def decode(cls, id):
        res = current_app.resources['Tag'].hashids.decode(id)
        if not res:
            raise ValueError('{} is not a valid Tag.'.format(id))
        return res[0]

    def __repr__(self) -> str:
        return '<Tag {0.id} device={0.device_id}>'.format(self)


class ETag(Tag):
    """
    A tag of the form {TAG_PROVIDER_ID}-{HASH}.
    """

    @property
    def id(self):
        return '{}-{}'.format(app.config['TAG_PROVIDER_ID'], super().id)

    @id.setter
    def id(self, id):
        self._id = self.decode(id)

    @classmethod
    def decode(cls, id):
        try:
            provider_id, hash = id.split('-')
        except ValueError:
            raise ValueError('Not an ETag.')
        if provider_id != app.config['TAG_PROVIDER_ID'].lower():
            raise UnprocessableEntity('The tag does not belong to this provider ID')
        return super().decode(hash)


class NoRemoteTag(BadRequest):
    description = 'This tag has not been assigned to a Devicehub.'


class Link(db.Model):
    """A Link to an URL.

    Stores URLs and provides a hashed ID back.
    """
    # todo develop
    id = Column(db.BigInteger, Sequence('link_id_seq'), primary_key=True)
    url = Column(URLType, nullable=False, unique=True)
    updated = db.Column(db.TIMESTAMP(timezone=True),
                        server_default=db.text('CURRENT_TIMESTAMP'),
                        nullable=False)
    created = db.Column(db.TIMESTAMP(timezone=True),
                        server_default=db.text('CURRENT_TIMESTAMP'),
                        nullable=False)
