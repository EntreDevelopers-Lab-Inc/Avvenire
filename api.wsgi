#!/usr/bin/python3.7
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/Locovotiv/")

from api import app as application
