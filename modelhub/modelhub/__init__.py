"""
Copyright 2021 Objectiv B.V.
"""
__version__ = '0.0.4'

from modelhub.modelhub import ModelHub
from modelhub.aggregate import Aggregate
from modelhub.map import Map
from modelhub.stack import *
from modelhub.series import *
from modelhub.models import *


# Here we do a basic version check, to make sure we are on the most recent versions of objectiv-bach and
# objectiv-modelhub. This is done by querying the backend that holds a cached version of the latest versions
# available from the pypi archive. These are compared with the local versions. If a newer version is available
# a Python warning is issued.
# To disable this, either set `OBJECTIV_VERSION_CHECK_DISABLE` in the environment, or suppress the warning.
#
# See: https://objectiv.io/docs/modeling/open-model-hub/version-check/` for more info

# we need this to check the environment variables
import os

# check env for opt-out setting
if os.environ.get('OBJECTIV_VERSION_CHECK_DISABLE', 'false') == 'false':
    try:
        # wrap the import in try/except to make sure we don't fail if there are missing imports
        import warnings
        import asyncio
        import aiohttp

        from bach import __version__ as bach_version

        CHECK_URL = os.environ.get('OBJECTIV_VERSION_CHECK_URL',
                                   'https://version-check.objectiv.io/check_version')

        async def check_package_version():
            packages = [
                    f'objectiv-bach:{bach_version}',
                    f'objectiv-modelhub:{__version__}'
            ]

            data = '\n'.join(packages)
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(CHECK_URL, data=data) as resp:
                        status = resp.status
                        if status == 200:
                            lines = await resp.text()
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
                # if this fails, we don't want to know
                pass

        try:
            # if there's an existing eventloop, we add a task to it, to run async, non-blocking
            loop = asyncio.get_running_loop()
            loop.create_task(check_package_version())
        except RuntimeError as re:
            try:
                # no loop, we create one of our own and run the version check, this is blocking
                asyncio.run(check_package_version())
            except Exception as e:
                pass
    except ModuleNotFoundError:
        # this can only happen if asyncio or aiohttp are not present
        pass
