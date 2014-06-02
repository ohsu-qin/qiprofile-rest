import os
import qiprofile_rest

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'sphinx.ext.todo']
autoclass_content = "both"
templates_path = ['templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'qiprofile-rest'
copyright = u'2014, OHSU Knight Cancer Institute'
pygments_style = 'sphinx'
html_theme = 'qiprofile_rest_theme'
html_theme_path = ['.']
html_theme_options = dict(linkcolor='DarkSkyBlue', visitedlinkcolor='Navy')
htmlhelp_basename = 'qiprofilerestdoc'
html_title = "qiprofile-rest"
