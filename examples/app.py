from ereuse_tag.auth import Auth
from ereuse_tag.config import Config as TagsConfig
from ereuse_tag.db import db
from teal.teal import Teal


class DeviceTagConf(TagsConfig):
    TAG_PROVIDER_ID = 'DT'
    TAG_HASH_SALT = '$6f/Wspgaswc1xJq5xj'
    SQLALCHEMY_DATABASE_URI = 'postgresql://dhub:4kbG7heYar6VDd@localhost/tags'
    DEVICEHUBS = {
        '899c794e-1737-4cea-9232-fdc507ab7106': 'http://127.0.0.1:5000',
        '9f564863-2d28-4b69-a541-a08c5b34d422': 'http://127.0.0.1:5000',
    }

app = Teal(config=DeviceTagConf(), db=db, Auth=Auth)
app.run(port=8081)
