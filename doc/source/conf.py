import os
import qipipe

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']
autoclass_content = "both"
source_suffix = '.rst'
master_doc = 'index'
project = u'qiprofile_rest'
copyright = u'2014, OHSU Knight Cancer Institute'
version = qiprofile.__version
pygments_style = 'sphinx'
html_theme = 'theme'
html_theme_path = ['.']
html_theme_options = dict(linkcolor='DarkSkyBlue', visitedlinkcolor='Navy')
htmlhelp_basename = 'qiprofilerestdoc'
html_title = "qiprofile_rest v%s" % version
