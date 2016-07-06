import os
import sys
import qiprofile_rest

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']
autoclass_content = "both"
autodoc_default_flags= ['members', 'show-inheritance']
source_suffix = '.rst'
master_doc = 'index'
project = u'qiprofile-rest'
copyright = u'2014, OHSU Knight Cancer Institute. This software is not intended for clinical use'
pygments_style = 'sphinx'
htmlhelp_basename = 'qiprofilerestdoc'
html_title = "qiprofile-rest"

def skip(app, what, name, obj, skip, options):
    return False if name == "__init__" else skip


def setup(app):
    app.connect("autodoc-skip-member", skip)
