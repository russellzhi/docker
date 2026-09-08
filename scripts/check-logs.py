"""Exercise PHP-FPM and MySQL logging, then read the host files as the current user."""
import concurrent.futures
import subprocess
import time
import uuid
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError

root = Path(__file__).resolve().parent.parent
marker = "log-check-" + uuid.uuid4().hex

def check_site(item):
    site, runtime, version = item
    filename = marker + ".php"
    path = root / "html" / ("demo%d.com" % site) / filename
    try:
        # Exclusive creation avoids overwriting any user file.
        with path.open("x", encoding="utf-8") as handle:
            handle.write("<?php error_log('%s'); sleep(7); echo PHP_VERSION;" % marker)
        with urlopen("http://127.0.0.1:800%d/%s" % (site, filename), timeout=20) as response:
            assert response.read().decode() == version
        try:
            urlopen("http://127.0.0.1:800%d/.env" % site, timeout=5)
        except HTTPError as error:
            assert error.code == 403
        else:
            raise AssertionError("Hidden file protection failed")
        checks = {
            "nginx/demo%d-access.log" % site: filename,
            "%s/access.log" % runtime: filename,
            "%s/error.log" % runtime: marker,
            "%s/slow.log" % runtime: filename,
        }
        # FPM flushes request logs just after completing the response.
        for relative, expected in checks.items():
            log = root / "logs" / relative
            for attempt in range(10):
                if log.exists() and expected in log.read_text(errors="replace"):
                    break
                time.sleep(0.2)
            else:
                raise AssertionError("Missing log record: " + relative)
        for relative in ["nginx/demo%d-error.log" % site, "%s/fpm-error.log" % runtime]:
            assert (root / "logs" / relative).read_text(errors="replace")
        print("demo%d: Nginx access/error and PHP error/access/slow/FPM logs OK" % site)
    finally:
        path.unlink(missing_ok=True)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(check_site, [(1, "php56", "5.6.40"), (2, "php74", "7.4.33"), (3, "php85", "8.5.10")]))

sql = "SELECT /* %s */ SLEEP(2.2);" % marker
subprocess.run(["docker", "compose", "exec", "-T", "mysql", "sh", "-c", 'MYSQL_PWD="$MYSQL_PASSWORD" mysql --comments -u demo -D demo',], input=sql, text=True, check=True, stdout=subprocess.DEVNULL)
assert marker in (root / "logs/mysql/slow.log").read_text(errors="replace")
assert (root / "logs/mysql/error.log").read_text(errors="replace")
print("MySQL error/slow logs OK; all log files readable by the host user")
