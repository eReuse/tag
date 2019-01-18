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

    def __init__(self, db: str = None) -> None:
        assert self.TAG_PROVIDER_ID, 'Set a TAG_PROVIDER_ID.'
        super().__init__(db)
