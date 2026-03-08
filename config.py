"""
HarvestHub — Application Configuration
---------------------------------------
Update MYSQL_PASSWORD and other settings to match your local MySQL setup.
"""

import os


class Config:
    # Flask secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'harvesthub-secret-key-change-in-production')

    # MySQL database settings
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 's6z3ud7e0f')  # <-- Set your MySQL root password here
    MYSQL_DB = os.environ.get('MYSQL_DB', 'harvesthub')
    MYSQL_CURSORCLASS = 'DictCursor'

    # Debug mode (disable in production)
    DEBUG = True
