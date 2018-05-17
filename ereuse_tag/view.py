from flask import Response, redirect, request
from marshmallow import ValidationError
from teal.resource import View
from werkzeug.exceptions import BadRequest

from ereuse_tag.model import Tag
from ereuse_tag.schema import Tag as TagS


class TagView(View):
    def one(self, id):
        """
        Redirects to the linked device or returns a HTTP 400 if
        no device has been linked yet.
        :param id: ID of the Tag.
        """
        tag = Tag.query.filter_by(id=id).one()  # type: Tag
        if not tag.same_as:
            raise TagNotLinked()
        return redirect(location=tag.same_as)

    def put(self, id: str):
        """
        Links a tag with a device in a DeviceHub.
        """
        # todo not tested
        t = request.get_json()  # type: dict
        tag = Tag.query.filter_by(id=id).one()  # type: Tag
        if tag.same_as:
            raise AlreadyLinked(tag.same_as)
        tag.same_as = t['same_as']
        return Response(status=204)


class TagNotLinked(BadRequest):
    description = 'This tag is not linked to a device.'


class AlreadyLinked(ValidationError):
    def __init__(self, same_as, **kwargs):
        message = 'This tag is already linked with device {}'.format(same_as)
        fields = TagS.same_as
        super().__init__(message, fields, **kwargs)
