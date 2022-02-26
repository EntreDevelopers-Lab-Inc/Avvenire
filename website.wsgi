#!/usr/bin/python3.8
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/beta/Avvenire/")

from website import app as application
