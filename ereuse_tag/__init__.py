import click
import csv as csvm
from boltons.urlutils import URL
from click import IntRange, argument, option
from teal.config import Config as TealConfig
from teal.resource import Converters, Resource

from ereuse_tag.model import Tag, db
from ereuse_tag.schema import Tag as TagS
from ereuse_tag.view import TagView


class TagDef(Resource):
    SCHEMA = TagS
    ID_CONVERTER = Converters.string
    VIEW = TagView

    def __init__(self, app, import_name=__package__, static_folder=None, static_url_path=None,
                 template_folder=None, url_prefix=None, subdomain=None, url_defaults=None,
                 root_path=None):
        cli_commands = ((self.create_tags, 'create-tags'),)
        super().__init__(app, import_name, static_folder, static_url_path, template_folder,
                         url_prefix, subdomain, url_defaults, root_path, cli_commands)

    @option('--csv',
            type=click.Path(dir_okay=False, writable=True, resolve_path=True),
            help='The path of a CSV file to save the IDs.')
    @option('--base-url', help='An URL to append to the IDs in the CSV without leading slash.')
    @argument('num', type=IntRange(1, 200))
    def create_tags(self, num: int, base_url: str, csv: str):
        """
        Creates NUM empty tags (only with the ID) and optionally saves
        a CSV of those new ids into a file.
        """
        # app_context() required (auto provided when in cli)
        assert URL(base_url) and base_url[-1] != '/', 'Provide a valid URL without leading slash.'
        tags = tuple(Tag() for _ in range(num))
        db.session.add_all(tags)
        db.session.commit()
        with open(csv, mode='w') as f:
            csv_writer = csvm.writer(f)
            for tag in tags:
                csv_writer.writerow(['{}/{}'.format(base_url, tag.id)])
        print('Created all tags and saved them in the CSV {}'.format(csv))


class Config(TealConfig):
    RESOURCE_DEFINITIONS = TagDef,
