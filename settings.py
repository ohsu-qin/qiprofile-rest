# This file specifies the Eve configuration.

MONGO_DBNAME = 'qiprofile'

# Even though the domain is defined by the Eve MongoEngine
# adapter, a DOMAIN setting is required by Eve. This setting
# is only used to avoid an Eve complaint about a missing domain.
DOMAIN = {'eve-mongoengine': {}}
