"""This ``settings`` file specifies the Eve configuration."""

import os

PROD_DBNAME = 'qiprofile'
"""The production database name."""

TEST_DBNAME = 'qiprofile_test'
"""The test/dev database name."""

# The run environment default is production.
# Modify this by setting the NODE_ENV environment variable.
env = os.getenv('NODE_ENV') or 'development'
# The MongoDB database.
if env == 'production':
    MONGO_DBNAME = PROD_DBNAME
else:
    MONGO_DBNAME = TEST_DBNAME

# The DYNO environment variable is a useful Heroku detection
# proxy. If on Heroku, then set the Heroku demo variables.
# TODO - get these settings from the Heroku environment.
# TODO - uncomment and retry a Heroku deployment.
# if 'DYNO' in os.environ:
#     MONGO_HOST = 'ds053139.mongolab.com'
#     MONGO_PORT = 53139
#     MONGO_USERNAME = 'seger'
#     MONGO_PASSWORD = 'library1'

# Look for MongoDB environment overrides:

# The default host is localhost.
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
