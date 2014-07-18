import importlib
import mongoengine
from eve import Eve
from eve_mongoengine import EveMongoengine
from qiprofile_rest import models

# The application. 
app = Eve()

# The MongoEngine ORM extension.
ext = EveMongoengine(app)

# Register the model non-embedded documdent classes.
ext.add_model(models.Subject, url='subjects')
ext.add_model(models.SubjectDetail, url='subject-detail')
ext.add_model(models.SessionDetail, url='session-detail')


if __name__ == '__main__':
    app.run()
