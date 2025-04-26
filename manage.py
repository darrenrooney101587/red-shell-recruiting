#!/usr/bin/env python
import os
import sys

def setup():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bms_admin.settings')
    try:
        from environment import load_env

        load_env()
    except ImportError as e:
        print("Unable to import the environment")
        pass


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app_admin.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
