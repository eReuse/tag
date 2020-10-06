import boltons.urlutils
from decouple import config
from itertools import chain

from teal.config import Config

from ereuse_tag.definition import TagDef, VersionDef


class TagsConfig(Config):
    DB_USER = config('DB_USER', 'dtag')
    DB_PASSWORD = config('DB_PASSWORD', 'ereuse')
    DB_HOST = config('DB_HOST', 'localhost')
    DB_DATABASE = config('DB_DATABASE', 'tags')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{pw}@{host}/{db}'.format(
        user=DB_USER, pw=DB_PASSWORD, host=DB_HOST, db=DB_DATABASE)  #type: str
    RESOURCE_DEFINITIONS = TagDef, VersionDef
    TAG_PROVIDER_ID = None
    """
    The eReuse.org Tag Provider ID for this instance.
    """
    TAG_HASH_SALT = None
    """
    Optional. Salt to make the generated tag ids impossible to
    decode for third-parties. Keep this private.

    If not set third-parties can decode the ID and get the number
    of the database behind it.
    """
    DEVICEHUBS = {}
    """
    A dict of devicehubs that have access to this tag. Values are
    the base url (scheme plus host) and keys are the token that
    identifies them.
    """
    API_DOC_CONFIG_TITLE = 'Tags'
    API_DOC_CONFIG_VERSION = '0.1'

    def __init__(self) -> None:
        assert self.TAG_PROVIDER_ID, 'Set a TAG_PROVIDER_ID.'
        assert self.DEVICEHUBS, 'Set at least one Devicehub'
        assert self.TAG_HASH_SALT, 'Set a Tag Hash salt'
        for token, url in self.DEVICEHUBS.items():
            assert url[-1] != '/', 'No final slash for Devicehub URL {}'.format(url)
            self.DEVICEHUBS[token] = boltons.urlutils.URL(url)
        super().__init__()
