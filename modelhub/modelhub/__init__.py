"""
Copyright 2021 Objectiv B.V.
"""
__version__ = '0.0.17'

from modelhub.modelhub import ModelHub
from modelhub.aggregate import Aggregate
from modelhub.map import Map
from modelhub.models.logistic_regression import LogisticRegression
from modelhub.pipelines import *
from modelhub.series import *


# Here we do a basic version check, to make sure we are on the most recent versions of objectiv-bach and
# objectiv-modelhub. This is done by querying the backend that holds a cached version of the latest versions
# available from the pypi archive. These are compared with the local versions. If a newer version is available
# a Python warning is issued.
# To disable this, either set `OBJECTIV_VERSION_CHECK_DISABLE` in the environment, or suppress the warning.
#
# See: https://objectiv.io/docs/modeling/open-model-hub/version-check/` for more info

# we need this to check the environment variables
import os


def check_version():
    # check env for opt-out setting
    if os.environ.get('OBJECTIV_VERSION_CHECK_DISABLE', 'false') != 'false':
        return
    try:
        # wrap the import in try/except to make sure we don't fail if there are missing imports
        import warnings
        import requests
        from bach import __version__ as bach_version

        check_url = os.environ.get('OBJECTIV_VERSION_CHECK_URL',
                                   'https://version-check.objectiv.io/check_version')
        packages = [
                f'objectiv-bach:{bach_version}',
                f'objectiv-modelhub:{__version__}'
        ]
        data = '\n'.join(packages)

        response = requests.post(check_url, data=data, timeout=5)
        lines = response.text
        for line in lines.split('\n'):
            items = line.split(':')
            # we expect at least 4 items, but the message may contain colons, so there
            # may be more items in the list. We combine the remaining ones into
            # one str: message
            if len(items) > 3:
                package, updated, version = items[:3]
                message = ':'.join(items[3:])
                # this is a line containing package:updated:version:message

                if updated == 'True':
                    warnings.warn(category=Warning, message=message)
    except Exception as e:
        pass


check_version()
