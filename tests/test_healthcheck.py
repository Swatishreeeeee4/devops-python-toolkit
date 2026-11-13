from devops_toolkit.healthcheck import is_up


def test_unreachable_url_is_down():
    assert is_up("http://127.0.0.1:9", retries=1, wait=0) is False
