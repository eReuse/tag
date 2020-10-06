import csv
from tempfile import NamedTemporaryFile

import pytest
from boltons.urlutils import URL
from ereuse_utils.test import ANY
from flask.testing import FlaskCliRunner
from teal.client import Client
from teal.teal import Teal
from werkzeug.exceptions import UnprocessableEntity

from ereuse_tag import __version__
from ereuse_tag import auth
from ereuse_tag.auth import Auth
from ereuse_tag.config import TagsConfig
from ereuse_tag.model import ETag, NoRemoteTag, Tag, db


@pytest.fixture
def app(request):
    class TestConfig(TagsConfig):
        SQLALCHEMY_DATABASE_URI = 'postgresql://dtag:ereuse@localhost/tagtest'
        # SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/tagtest'
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
        assert t.devicehub is None
        assert t.id == '3MP5M'

        et = ETag()
        db.session.add(et)
        db.session.commit()
        assert et.id == 'FO-WNBRM'
        assert et.id.split('-')[0] == 'FO'
        assert len(et.id.split('-')[1]) == 5
        assert et.devicehub is None


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
        result = runner.invoke(args=('create-tags', '100', '--csv', f.name, '--etag'),
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
    assert response.location == 'https://dh.com/tags/{}/device'.format(res[0])


def test_get_wrong_url(client: Client):
    client.get('/', item='foobar', status=404, accept=ANY)


def test_tag_export(runner: FlaskCliRunner, app: Teal):
    with app.app_context():
        t = ETag()
        db.session.add(t)
        db.session.commit()
    with NamedTemporaryFile('r+') as f:
        result = runner.invoke(args=('export', f.name), catch_exceptions=False)
        assert result.exit_code == 0
        result = runner.invoke(args=('import', f.name), catch_exceptions=False)
        assert result.exit_code == 0
    with app.app_context():
        t = Tag()
        db.session.add(t)
        db.session.commit()
        assert Tag.decode(t.id) == 2


def test_etag_secondary(client: Client, app: Teal):
    """Tests creating, linking and accessing an ETag through
    its secondary (NFC) id."""
    with app.app_context():
        et = ETag(secondary='NFCID')
        db.session.add(et)
        db.session.commit()
    client.get('/', item='NFCID', accept=ANY, status=400)
    with app.app_context():
        tag = ETag.query.filter_by(secondary='NFCID').one()
        tag.devicehub = URL('https://dh.com')
        db.session.commit()
    _, r = client.get('/', item='NFCID', accept=ANY, status=302)
    assert r.location == 'https://dh.com/tags/FO-3MP5M/device'


@pytest.mark.mvp
def test_get_version(app: Teal, client: Client):
    """Checks GETting versions of service."""

    content, res = client.get("/versions/version/", None)

    assert res.status_code == 200
    assert content == {'ereuse_tag': __version__}
