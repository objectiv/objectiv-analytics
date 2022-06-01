import os
from modelhub import check_version

request_counter = 0


def test_disable_version_check(monkeypatch):
    # patch requests.post so we never do a request
    def custom_post(*args, **kwargs):
        global request_counter
        request_counter += 1

    monkeypatch.setattr('requests.post', custom_post)

    original_version_check_disable = os.environ.get('OBJECTIV_VERSION_CHECK_DISABLE', None)

    # disable the version check
    os.environ['OBJECTIV_VERSION_CHECK_DISABLE'] = 'true'
    old_request_counter = request_counter
    check_version()

    # check that we didn't do a request
    assert request_counter == old_request_counter

    os.environ['OBJECTIV_VERSION_CHECK_DISABLE'] = 'false'
    old_request_counter = request_counter
    check_version()

    # check that we did do a request
    assert request_counter == old_request_counter + 1

    # restore version check setting
    if original_version_check_disable:
        os.environ['OBJECTIV_VERSION_CHECK_DISABLE'] = original_version_check_disable
