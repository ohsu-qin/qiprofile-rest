#!/usr/bin/env python
"""
Controls the QIN Profile web app.
"""
import os
import sys
from django.core import management


def main(argv=sys.argv):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qiprofile.settings')
    management.execute_from_command_line(sys.argv)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
