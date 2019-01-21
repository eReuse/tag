import teal.auth
import werkzeug.exceptions
from flask import current_app


class Auth(teal.auth.TokenAuth):
    def authenticate(self, token: str, *args, **kw) -> object:
        try:
            return current_app.config['DEVICEHUBS'][token]
        except KeyError:
            raise werkzeug.exceptions.Unauthorized('Provide a suitable token.')
