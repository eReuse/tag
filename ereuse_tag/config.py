import boltons.urlutils
import teal.config

from ereuse_tag.definition import TagDef


class Config(teal.config.Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql://dtag:ereuse@localhost/tag'  # type: str
    RESOURCE_DEFINITIONS = TagDef,
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

    def __init__(self) -> None:
        assert self.TAG_PROVIDER_ID, 'Set a TAG_PROVIDER_ID.'
        assert self.DEVICEHUBS, 'Set at least one Devicehub'
        assert self.TAG_HASH_SALT, 'Set a Tag Hash salt'
        for token, url in self.DEVICEHUBS.items():
            assert url[-1] != '/', 'No final slash for Devicehub URL {}'.format(url)
            self.DEVICEHUBS[token] = boltons.urlutils.URL(url)
        super().__init__()
