#!/usr/bin/env python
"""
Controls the QIN Profile web app.
"""
import sys
import os
import re


def main(argv=sys.argv):
    # The install command is handled here. Otherwise, delegate to Django.
    if len(argv) == 2 and argv[1] == 'install':
        return _install()
    else:
        return _delegate_to_django()


def _delegate_to_django():
    from django.core import management
    
    # Tell Django where to find the application configuration.
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'qiprofile_rest.settings'
    # Delegate to Django.
    management.execute_from_command_line(argv)
    
    return 0


def _install():
    import subprocess
    
    # The pattern for requirements which are supported by setup.py.
    setup_re = re.compile('[-\w]+(==[-\w.]+)?$')
    # The requirements file.
    rqmts_file = os.path.dirname(__file__) + '/requirements.txt'
    # All requirements.
    with open(rqmts_file) as f:
        rqmts = f.read().splitlines()
    # Install the non-setup requirements.
    for rqmt in rqmts:
        if not setup_re.match(rqmt):
            subprocess.call(['pip', 'install', rqmt])
    
    # Work around the following django-mongodb-engine bug:
    # * Installation of django-mongodb-engine fails if DJANGO_SETTINGS_MODULE
    #   is not set to either the empty string or an installed package, even
    #   though django-mongodb-engine install does not need the package settings.
    #   DJANGO_SETTINGS_MODULE can neither be unset nor can it be set to None.
    #   The work-around is to set DJANGO_SETTINGS_MODULE to the empty string
    #   during the django-mongodb-engine installation.
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = ''
    # Make the qiprofile-rest install command.
    p = subprocess.Popen(['pip', 'install', '-e', os.path.dirname(__file__)], env=env)
    # Run the command.
    p.wait()
    
    return p.returncode


if __name__ == "__main__":
    sys.exit(main())
