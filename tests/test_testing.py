import csv
from tempfile import NamedTemporaryFile

import pytest
from boltons.urlutils import URL
from ereuse_utils.test import ANY
from flask.testing import FlaskCliRunner
from teal.client import Client
from teal.teal import Teal
from werkzeug.exceptions import UnprocessableEntity

from ereuse_tag import auth
from ereuse_tag.auth import Auth
from ereuse_tag.config import Config
from ereuse_tag.model import NoRemoteTag, Tag, db


@pytest.fixture
def app(request):
    class TestConfig(Config):
        SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/tagtest'
        TAG_PROVIDER_ID = 'FO'
        TAG_HASH_SALT = 'So salty'
        SERVER_NAME = 'foo.bar'
        TESTING = True
        DEVICEHUBS = {'soToken': 'https://dh.com'}

    app = Teal(config=TestConfig(), db=db, Auth=Auth)
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


def test_tag_creation(app: Teal):
    with app.app_context():
        t = Tag()
        db.session.add(t)
        db.session.commit()
        assert t.id
        assert t.id.split('-')[0] == 'FO'
        assert len(t.id.split('-')[1]) == 5
        assert t.devicehub is None


def test_get_not_linked_tag(app: Teal, client: Client):
    """Tests getting a tag that has not been linked yet to a Devicehub."""
    with app.app_context():
        t = Tag()
        db.session.add(t)
        db.session.commit()
        id = t.id
    client.get(res=Tag.t, item=id, status=NoRemoteTag)


def test_create_tags_cli(runner: FlaskCliRunner, client: Client):
    """Tests creating a tag."""
    with NamedTemporaryFile('r+') as f:
        result = runner.invoke(args=('create-tags', '100', '--csv', f.name),
                               catch_exceptions=False)
        assert result.exit_code == 0
        urls = tuple(csv.reader(f))
        assert len(urls) == 100
        for url, *_ in urls:
            assert 'http://foo.bar/' in url
            assert len(url) == 23
            # Tag exists but it has not been linked
            client.get(res=Tag.t, item=URL(url).path_parts[1], status=NoRemoteTag)


def test_create_tags_endpoint_get(app: Teal, client: Client):
    """Tests creating regular tags through the endpoint and gets a
    tag.
    """
    token = auth.Auth.encode('soToken')
    res, _ = client.post({}, '/', query=[('num', 2)], token=token)
    client.post({}, '/', query=[('num', 0)], token=token, status=UnprocessableEntity)
    client.post({}, '/', query=[('num', -1)], token=token, status=UnprocessableEntity)
    client.post({}, '/', query=[('num', 101)], token=token, status=UnprocessableEntity)
    _, response = client.get('/', item=res[0], status=302, accept=ANY)
    assert response.location == 'https://dh.com/tags/{}'.format(res[0])


def test_tag_export(runner: FlaskCliRunner, app: Teal):
    with app.app_context():
        t = Tag()
        db.session.add(t)
        db.session.commit()
    with NamedTemporaryFile('r+') as f:
        result = runner.invoke(args=('export-tags', f.name), catch_exceptions=False)
        assert result.exit_code == 0
        result = runner.invoke(args=('import-tags', f.name), catch_exceptions=False)
        assert result.exit_code == 0
