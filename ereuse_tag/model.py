from datetime import datetime

import nanoid
from sqlalchemy import Column, Unicode
from teal.db import SQLAlchemy, URL

db = SQLAlchemy()


class Tag(db.Model):
    id = Column(Unicode, primary_key=True, default=lambda: Tag.gen_id())
    same_as = Column(URL)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def gen_id():
        id = nanoid.generate(size=14)
        assert not id.isnumeric()
        return id

    def __repr__(self) -> str:
        return '<Tag {0.id} same_as={0.same_as!r}>'.format(self)
