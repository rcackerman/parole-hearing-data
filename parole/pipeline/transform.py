'''
Transform raw parolee scrape information.
'''

import os
import yaml

_CONFIG_DIR = os.path.join(os.path.dirname(
                            os.path.dirname(__file__)
                            ), 'config')
_SECURITY_LEVELS = yaml.load(
                    open(os.path.join(_CONFIG_DIR, 'prisons.yml')))
_SIMPLIFIED_DECISIONS = yaml.load(
                            open(os.path.join(_CONFIG_DIR, 'decisions.yml')))
_FORBIDDEN_HEADERS = [u'inmate name']
