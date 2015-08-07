"""This ``settings`` file specifies the Eve configuration."""

import os

# The run environment default is production.
# Modify this by setting the NODE_ENV environment variable.
env = os.getenv('NODE_ENV') or 'production'
# The MongoDB database.
if env == 'production':
    MONGO_DBNAME = 'qiprofile'
else:
    MONGO_DBNAME = 'qiprofile_test'

# The MongoDB host default is localhost, but can be reset
# by the MONGO_HOST environment variable.
host = os.getenv('MONGO_HOST')
if host:
    MONGO_HOST = host

# The MongoDB port.
port = os.getenv('MONGO_PORT')
if port:
    MONGO_PORT = int(port)

# The MongoDB username.
user = os.getenv('MONGO_USERNAME')
if user:
    MONGO_USERNAME = user

# The MongoDB password.
pswd = os.getenv('MONGO_PASSWORD')
if pswd:
    MONGO_PASSWORD = pswd

# Even though the domain is defined by the Eve MongoEngine
# adapter, a DOMAIN setting is required by Eve. This setting
# is only used to avoid an Eve complaint about a missing domain.
DOMAIN = {'eve-mongoengine': {}}
