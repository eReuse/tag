"""
Example app with minimal configuration.

Use this as a starting point.
"""
from teal.teal import Teal

from ereuse_tag.auth import Auth
from ereuse_tag.config import Config
from ereuse_tag.db import db


class MyConfig(Config):
    TAG_PROVIDER_ID = 'foo'
    TAG_HASH_SALT = 'bar'


app = Teal(MyConfig(), db=db, Auth=Auth)
