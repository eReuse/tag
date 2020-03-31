from ereuse_tag.auth import Auth
from ereuse_tag.config import TagsConfig
from ereuse_tag.db import db
from teal.teal import Teal
from teal.auth import TokenAuth


class DeviceTagConf(TagsConfig):
    TAG_PROVIDER_ID = 'DT'
    TAG_HASH_SALT = '$6f/Wspgaswc1xJq5xj'
    SQLALCHEMY_DATABASE_URI = 'postgresql://dtag:f4j3fx8z@localhost/tags'
    DEVICEHUBS = {
        '7ad6eb73-d95c-4cdf-bf9f-b33be4e514b3': 'http://localhost:5000/testdb'
    }
    API_DOC_CONFIG_TITLE = 'Tags'
    API_DOC_CONFIG_VERSION = '0.1'
    API_DOC_CONFIG_COMPONENTS = {
        'securitySchemes': {
            'bearerAuth': TokenAuth.API_DOCS
        }
    }
    API_DOC_CLASS_DISCRIMINATOR = 'type'


app = Teal(config=DeviceTagConf(), db=db, Auth=Auth)

