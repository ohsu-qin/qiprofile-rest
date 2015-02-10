#!/usr/bin/env python
import importlib
import mongoengine
from eve import Eve
from eve_mongoengine import EveMongoengine
from qiprofile_rest.model.subject import Subject
from qiprofile_rest.model.imaging import SessionDetail

# The application. 
app = Eve()

# The MongoEngine ORM extension.
ext = EveMongoengine(app)

# Register the model non-embedded documdent classes.
ext.add_model(Subject, url='subject')
ext.add_model(SessionDetail, url='session-detail')


if __name__ == '__main__':
    app.run()
