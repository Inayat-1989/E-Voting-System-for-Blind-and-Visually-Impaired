#!/usr/bin/env python
import dotenv

import os
import sys

dotenv.load_dotenv()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "evoting_project.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
