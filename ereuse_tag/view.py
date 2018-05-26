from flask import redirect
from teal.resource import View

from ereuse_tag.model import Tag


class TagView(View):
    def one(self, id):
        """
        Redirects to the linked device or returns a HTTP 400 if
        no device has been linked yet.
        :param id: ID of the Tag.
        """
        tag = Tag.query.filter_by(id=id).one()  # type: Tag
        return redirect(location=tag.remote_tag.to_text())
