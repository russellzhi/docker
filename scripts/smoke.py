"""Run after docker compose up -d --build: python3 scripts/smoke.py."""
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import time

for site, version in [(1, "5.6.40"), (2, "7.4.33"), (3, "8.5.10")]:
    base = "http://127.0.0.1:800%d" % site
    # Allow a short startup/DNS refresh window after containers are recreated.
    for attempt in range(20):
        try:
            with urlopen(base, timeout=5) as response:
                page = response.read().decode("utf-8")
                assert response.status == 200
            assert "PHP " + version in page, (site, "Unexpected PHP version")
            break
        except (URLError, AssertionError):
            if attempt == 19:
                raise
            time.sleep(0.5)
    for row_id, suffix in [(1, "A"), (2, "B")]:
        expected = "<tr><td>%d</td><td>demo%d-%s</td></tr>" % (row_id, site, suffix)
        assert expected in page, (site, "Missing database row", expected)
    for path, expected_status in [("/.env", 403), ("/missing.php", 404), ("/missing.png", 404)]:
        try:
            urlopen(base + path, timeout=10)
        except HTTPError as error:
            assert error.code == expected_status, (site, path, error.code)
        else:
            raise AssertionError((site, path, "Unexpected successful response"))
    print("demo%d: PHP %s, database rows and HTTP protections OK" % (site, version))
