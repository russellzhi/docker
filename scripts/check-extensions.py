"""Verify extension loading and representative operations in all three PHP runtimes."""
import subprocess
import sys

required = "bcmath bz2 calendar ctype curl dom exif fileinfo ftp gd gettext gmp iconv intl json ldap mbstring mysqli openssl PDO pdo_mysql pdo_pgsql pdo_sqlite pgsql pcntl redis apcu imagick shmop SimpleXML soap sockets sqlite3 sysvmsg sysvsem sysvshm tidy tokenizer xml xmlreader xmlwriter xsl zip zlib".split()
for service in (sys.argv[1:] or ["php56", "php74", "php85"]):
    extensions = required + (["mysql", "mcrypt"] if service == "php56" else ["sodium"])
    php = "foreach (explode(' ', '%s') as $ext) { if (!extension_loaded($ext)) { fwrite(STDERR, 'Missing: '.$ext.PHP_EOL); exit(1); } }" % " ".join(extensions)
    php += r"""
if (!extension_loaded('Zend OPcache')) { throw new Exception('OPcache missing'); }
if (bcadd('1.2', '2.3', 1) !== '3.5') { throw new Exception('BCMath failed'); }
if (gmp_strval(gmp_add('100', '23')) !== '123') { throw new Exception('GMP failed'); }
if (!Normalizer::isNormalized(Normalizer::normalize('test'))) { throw new Exception('Intl failed'); }
$image = imagecreatetruecolor(4, 4);
if (!imagepng($image, '/tmp/extension-check.png')) { throw new Exception('GD failed'); }
$imagick = new Imagick('/tmp/extension-check.png');
if ($imagick->getImageWidth() !== 4) { throw new Exception('Imagick failed'); }
unlink('/tmp/extension-check.png');
$zip = new ZipArchive();
if ($zip->open('/tmp/extension-check.zip', ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) { throw new Exception('ZIP failed'); }
$zip->addFromString('check.txt', 'ok');
$zip->close();
$zip->open('/tmp/extension-check.zip');
if ($zip->getFromName('check.txt') !== 'ok') { throw new Exception('ZIP round trip failed'); }
$zip->close();
unlink('/tmp/extension-check.zip');
if (!apcu_store('extension-check', 'ok') || apcu_fetch('extension-check') !== 'ok') { throw new Exception('APCu failed'); }
apcu_delete('extension-check');
$redis = new Redis();
echo PHP_VERSION.' extensions and functional checks OK'.PHP_EOL;
"""
    subprocess.run(["docker", "compose", "exec", "-T", service, "php", "-d", "apc.enable_cli=1", "-r", php], check=True)
