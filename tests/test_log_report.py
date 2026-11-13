from devops_toolkit.log_report import analyse

SAMPLE = [
    '10.0.0.1 - - [13/Nov/2026:10:00:00 +0000] "GET /login HTTP/1.1" 200 512 "-" "curl"\n',
    '10.0.0.1 - - [13/Nov/2026:10:00:01 +0000] "POST /login?x=1 HTTP/1.1" 302 0 "-" "curl"\n',
    '10.0.0.2 - - [13/Nov/2026:10:00:02 +0000] "GET /api/users HTTP/1.1" 500 12 "-" "curl"\n',
    '10.0.0.3 - - [13/Nov/2026:10:00:03 +0000] "GET /missing HTTP/1.1" 404 0 "-" "curl"\n',
    "this line is not an access log line\n",
]


def test_counts_and_error_rate():
    r = analyse(SAMPLE, top=2)
    assert r.total == 4
    assert r.unparsed == 1
    assert r.by_status_class == {"2xx": 1, "3xx": 1, "4xx": 1, "5xx": 1}
    assert r.error_rate_5xx == 25.0


def test_top_ips_and_paths_strip_query_string():
    r = analyse(SAMPLE, top=1)
    assert r.top_ips == [("10.0.0.1", 2)]
    assert r.top_paths == [("/login", 2)]


def test_empty_log():
    r = analyse([])
    assert r.total == 0 and r.error_rate_5xx == 0.0
