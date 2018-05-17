import csv
from tempfile import NamedTemporaryFile

import pytest
from boltons.urlutils import URL
from flask.testing import FlaskCliRunner
from teal.client import Client
from teal.teal import Teal

from ereuse_tag import Config
from ereuse_tag.model import Tag, db
from ereuse_tag.view import TagNotLinked


@pytest.fixture
def app(request):
    class TestConfig(Config):
        SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/et_test'
        TESTING = True

    app = Teal(config=TestConfig(), db=db)
    db.create_all(app=app)
    # More robust than 'yield'
    request.addfinalizer(lambda *args, **kw: db.drop_all(app=app))
    return app


@pytest.fixture()
def runner(app: Teal) -> FlaskCliRunner:
    return app.test_cli_runner()


@pytest.fixture()
def client(app: Teal) -> Client:
    return app.test_client()


def test_create_tags_cli(runner: FlaskCliRunner, client: Client):
    """Tests creating a tag."""
    with NamedTemporaryFile('r+') as f:
        result = runner.invoke(args=('create-tags', '100',
                                     '--csv', f.name,
                                     '--base-url', 'http://foo.bar'),
                               catch_exceptions=False)
        assert result.exit_code == 0
        urls = tuple(csv.reader(f))
        assert len(urls) == 100
        for url, *_ in urls:
            assert 'http://foo.bar/' in url
            assert len(url) == 29
            # Tag exists but it has not been linked
            client.get(res=Tag.t, item=URL(url).path_parts[1], status=TagNotLinked)


def test_get_not_linked_tag(app: Teal, client: Client):
    """Tests getting a tag that has not been linked yet."""
    with app.app_context():
        t = Tag()
        db.session.add(t)
        db.session.commit()
        id = t.id
    client.get(res=Tag.t, item=id, status=TagNotLinked)


def test_link_tag():
    """Tests linking and reading a linked tag."""
    pass
    # todo
