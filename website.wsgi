#!/usr/bin/python3.7
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/MobileFirehouseFitness/")

from site import app as application
