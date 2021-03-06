import json

from flask import g, redirect, request
from flask.json import jsonify
from teal.resource import View
from werkzeug.exceptions import NotFound, UnprocessableEntity

from ereuse_tag import __version__
from ereuse_tag import auth
from ereuse_tag.db import db
from ereuse_tag.model import ETag, Tag


class TagView(View):
    def one(self, id):
        """
        Redirects to the linked device or returns a HTTP 400 if
        no device has been linked yet.
        :param id: ID of the Tag.
        """
        try:
            _id = ETag.decode(id)
        except ValueError:  # not an etag
            try:
                _id = Tag.decode(id)
            except ValueError:  # not the id of a tag
                # Is the secondary ID?
                tag = Tag.query.filter_by(secondary=id).one()
            else:
                tag = Tag.query.filter_by(_id=_id).one()  # type: Tag
        else:
            tag = Tag.query.filter_by(_id=_id).one()  # type: Tag
        return redirect(location=tag.remote_device.to_text())

    @auth.Auth.requires_auth
    def post(self):
        num = request.args.get('num', type=int)
        if not (0 < num <= 100):
            raise UnprocessableEntity('Num must be a natural not greater than 100.')
        tags = tuple(Tag(devicehub=g.user) for _ in range(num))
        db.session.add_all(tags)
        db.session.commit()
        ids = tuple(tag.id for tag in tags)
        response = jsonify(ids)
        response.status_code = 201
        return response


class VersionView(View):
    def get(self, *args, **kwargs):
        """Get version."""

        return json.dumps({'ereuse_tag': __version__})
