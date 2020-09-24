import csv as csvm
from pathlib import Path
from typing import Callable, Iterable, Tuple

from boltons.urlutils import URL
from click import IntRange, argument, option
from ereuse_utils import cli
from hashids import Hashids
from sqlalchemy import between
from teal.resource import Converters, Resource, url_for_resource

from ereuse_tag.model import ETag, Tag, db
from ereuse_tag.view import TagView, VersionView


class TagDef(Resource):
    __type__ = 'Tag'
    ID_CONVERTER = Converters.string
    VIEW = TagView
    TAG_HASH_ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    TAG_HASH_MIN = 5
    CLI_PATH = cli.Path(dir_okay=False, writable=True)

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
            (self.set_tags, 'set-tags'),
            (self.export_tags, 'export'),
            (self.import_tags, 'import')
        )
        super().__init__(app, import_name, static_folder, static_url_path, template_folder,
                         url_prefix, subdomain, url_defaults, root_path, cli_commands)
        self.hashids = Hashids(salt=app.config['TAG_HASH_SALT'],
                               min_length=self.TAG_HASH_MIN,
                               alphabet=self.TAG_HASH_ALPHABET)

    @option('--csv',
            type=CLI_PATH,
            help='The path of a CSV file to save the IDs.')
    @option('--etag/--no-etag', default=False, help='Generate eTags instead of regular tags.')
    @argument('num', type=IntRange(1))
    def create_tags(self, num: int, csv: Path, etag: bool):
        """
        Creates NUM empty tags (only with the ID) and optionally saves
        a CSV of those new ids into a file.
        """
        T = ETag if etag else Tag
        tags = tuple(T() for _ in range(num))
        db.session.add_all(tags)
        db.session.commit()
        self.tags_to_csv(csv, tags)
        print('Created all tags and saved them in the CSV {}'.format(csv))

    @option('--csv',
            type=CLI_PATH,
            help='The path of a CSV file to save the tags that were set.')
    @argument('ending-tag', type=IntRange(2))
    @argument('starting-tag', type=IntRange(1))
    @argument('devicehub')
    def set_tags(self, devicehub: str, starting_tag: int, ending_tag: int, csv: Path):
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
        self.tags_to_csv(csv, tags)
        print('All tags set to {}'.format(devicehub))

    @staticmethod
    def tags_to_csv(path: Path, tags: Iterable[Tag]):
        """
        Generates tags
        :param path:
        :param tags:
        :return:
        """
        with path.open('w') as f:
            csv_writer = csvm.writer(f)
            for tag in tags:
                csv_writer.writerow([url_for_resource(Tag, tag.id)])

    @argument('csv', type=CLI_PATH)
    def export_tags(self, csv: Path):
        """Exports the Tag database in a CSV file.  The rows are:
        ``id``, ``secondary``, ``devicehub``, ``type``, ``updated``, ``created``.
        """
        with csv.open('w') as f:
            csv_writer = csvm.writer(f)
            for tag in Tag.query:
                dh = tag.devicehub.to_url() if tag.devicehub else None
                row = tag.id, tag.secondary, dh, tag.type, tag.updated, tag.created
                csv_writer.writerow(row)

    @argument('csv', type=CLI_PATH)
    def import_tags(self, csv: Path):
        """Imports the database from a CSV from ``export``.
        This truncates only the Tag table.
        """
        db.session.execute('TRUNCATE TABLE {} RESTART IDENTITY'.format(Tag.__table__.name))
        max_id = 0
        """The maximum ID of the tags. Sequence is reset to this + 1."""
        with csv.open() as f:
            for row in csvm.reader(f):
                id, secondary, dh, type, updated, created = row
                cls = Tag if type == 'Tag' else ETag
                dh = URL(dh) if dh else None
                t = cls(id=id, secondary=secondary)
                db.session.add(t)
                max_id = max(max_id, cls.decode(id))
        db.session.execute('ALTER SEQUENCE tag_id RESTART WITH {}'.format(max_id + 1))
        db.session.commit()


class VersionDef(Resource):
    __type__ = 'Version'
    SCHEMA = None
    VIEW = None  # We do not want to create default / documents endpoint
    AUTH = False

    def __init__(self, app,
                 import_name=__name__,
                 static_folder=None,
                 static_url_path=None,
                 template_folder=None,
                 url_prefix=None,
                 subdomain=None,
                 url_defaults=None,
                 root_path=None,
                 cli_commands: Iterable[Tuple[Callable, str or None]] = tuple()):
        super().__init__(app, import_name, static_folder, static_url_path, template_folder,
                         url_prefix, subdomain, url_defaults, root_path, cli_commands)

        defaults = {'ereuse_tag': '0.0.0'}
        get = {'GET'}

        version_view = VersionView.as_view('VersionView', definition=self)
        self.add_url_rule('/version/', defaults=defaults, view_func=version_view, methods=get)
