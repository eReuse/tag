import csv as csvm
from pathlib import Path
from typing import Iterable

import click
from boltons.urlutils import URL
from click import IntRange, argument, option
from ereuse_tag.model import Tag, db
from ereuse_tag.view import TagView
from hashids import Hashids
from sqlalchemy import between
from teal.config import Config as TealConfig
from teal.resource import Converters, Resource, url_for_resource


class TagDef(Resource):
    __type__ = 'Tag'
    ID_CONVERTER = Converters.string
    VIEW = TagView
    TAG_HASH_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    TAG_HASH_MIN = 5

    def __init__(self, app,
                 import_name=__package__,
                 static_folder=None,
                 static_url_path=None,
                 template_folder=None,
                 url_prefix='',
                 subdomain=None,
                 url_defaults=None,
                 root_path=None):
        cli_commands = (
            (self.create_tags, 'create-tags'),
            (self.set_tags, 'set-tags')
        )
        super().__init__(app, import_name, static_folder, static_url_path, template_folder,
                         url_prefix, subdomain, url_defaults, root_path, cli_commands)
        self.hashids = Hashids(salt=app.config['TAG_HASH_SALT'],
                               min_length=self.TAG_HASH_MIN,
                               alphabet=self.TAG_HASH_ALPHABET)

    @option('--csv',
            type=click.Path(dir_okay=False, writable=True, resolve_path=True),
            help='The path of a CSV file to save the IDs.')
    @argument('num', type=IntRange(1))
    def create_tags(self, num: int, csv: str):
        """
        Creates NUM empty tags (only with the ID) and optionally saves
        a CSV of those new ids into a file.
        """
        tags = tuple(Tag() for _ in range(num))
        db.session.add_all(tags)
        db.session.commit()
        self.tags_to_csv(Path(csv), tags)
        print('Created all tags and saved them in the CSV {}'.format(csv))

    @option('--csv',
            type=click.Path(dir_okay=False, writable=True, resolve_path=True),
            help='The path of a CSV file to save the tags that were set.')
    @argument('ending-tag', type=IntRange(2))
    @argument('starting-tag', type=IntRange(1))
    @argument('devicehub')
    def set_tags(self, devicehub: str, starting_tag: int, ending_tag: int, csv: str):
        """
        "Sends" the tags to the specific devicehub,
        so they can only be linked in that devicehub.

        Actual implementation does not send them but rather update the
        internal database as it did send them. You will need to create
        them manually in the destination devicehub.

        This method in the future will probably actually (virtually)
        send them.
        """
        assert starting_tag < ending_tag
        assert URL(devicehub) and devicehub[-1] != '/', 'Provide a valid URL without leading slash'
        tags = Tag.query.filter(between(Tag.id, starting_tag, ending_tag)).all()
        for tag in tags:
            tag.devicehub = devicehub
        db.session.commit()
        self.tags_to_csv(Path(csv), tags)
        print('All tags set to {}'.format(devicehub))

    @staticmethod
    def tags_to_csv(path: Path, tags: Iterable[Tag]):
        with path.open('w') as f:
            csv_writer = csvm.writer(f)
            for tag in tags:
                csv_writer.writerow([url_for_resource(tag, tag.id)])


class Config(TealConfig):
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
