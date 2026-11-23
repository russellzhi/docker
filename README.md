# PHP 多版本 Docker 开发环境

| 站点 | 地址 | PHP | 数据表 |
| --- | --- | --- | --- |
| demo1 | http://localhost:8001 | 5.6.40（5.6 最终版） | demo.demo1 |
| demo2 | http://localhost:8002 | 7.4.33 | demo.demo2 |
| demo3 | http://localhost:8003 | 8.6.0 | demo.demo3 |

在 WSL 项目目录执行：

```sh
docker compose up -d --build
docker compose ps
python3 scripts/smoke.py
python3 scripts/check-extensions.py
python3 scripts/check-logs.py
```

日志检查脚本会临时创建测试 PHP 文件并在结束后清理，产生一次 7 秒的慢请求和 2.2 秒的慢查询，以验证日志确实落盘。

使用 `docker compose down` 停止。首次扩展构建需要访问 Docker Hub、Debian 软件源、PECL，三个版本均有较多编译步骤。

## 日志

所有日志保存在当前项目的 `logs` 目录。启动脚本会自动创建日志文件并配置容器内用户的写入权限。

| 路径 | 内容 |
| --- | --- |
| logs/nginx/demo1-access.log、demo2-access.log、demo3-access.log | 每个站点的 HTTP 访问日志 |
| logs/nginx/demo1-error.log、demo2-error.log、demo3-error.log | 每个站点的 Nginx 错误日志 |
| logs/nginx/error.log | Nginx 全局错误日志 |
| logs/php56、logs/php74、logs/php86 下的 error.log | PHP 应用错误日志 |
| 同目录 fpm-error.log | PHP-FPM 进程日志和工作进程标准输出 |
| 同目录 access.log | PHP-FPM 请求日志 |
| 同目录 slow.log | 超过 5 秒请求的堆栈日志 |
| logs/mysql/error.log | MySQL 错误日志 |
| logs/mysql/slow.log | 超过 2 秒的慢查询日志 |

例如：

```sh
tail -f logs/nginx/demo1-access.log logs/php56/error.log
tail -f logs/mysql/error.log
```

为了让 FPM 能抓取慢请求堆栈，PHP 容器增加 SYS_PTRACE 能力，仅用于本地诊断。

容器启动阶段输出仍可用 `docker compose logs` 查看。Docker 自身日志的 10MB/3 文件限制不适用于这些映射文件；映射日志需按使用量定期归档。未开启记录每条 SQL 的 general log。框架自行配置的应用日志仍写在框架指定目录。

## 扩展

三个版本共同覆盖：

- 数据库：PDO、pdo_mysql、mysqli、pdo_pgsql、pgsql、pdo_sqlite、sqlite3。
- 文本与 Web：mbstring、intl、iconv、curl、openssl、fileinfo、ctype、tokenizer、JSON。
- XML 与集成：DOM、SimpleXML、XMLReader、XMLWriter、SOAP、XSL、LDAP、Tidy。
- 图片与压缩：GD（JPEG、PNG、FreeType；7.4/8.6 额外支持 WebP）、Imagick、EXIF、ZIP、BZ2、zlib。
- 数学与系统：BCMath、GMP、calendar、gettext、FTP、sockets、pcntl、shmop、sysvmsg、sysvsem、sysvshm。
- 缓存：OPcache、Redis、APCu。

PHP 5.6 额外提供旧框架使用的 mysql、mcrypt。PHP 7.4/8.6 保留内置 sodium。PHP 8.6 的 OPcache 已内置，无需重复编译。

三个 PHP 容器通过只读挂载共用 php/browscap.ini，供 get_browser() 根据 User-Agent 查询浏览器特征。

PECL 扩展固定版本：PHP 5.6 使用 Redis 4.3.0、APCu 4.0.11；PHP 7.4 使用 Redis 6.3.0、APCu 5.1.28；PHP 5.6/7.4 使用 Imagick 3.8.1；PHP 8.6 的 Redis、APCu 和 Imagick 使用固定在 php/php86/Dockerfile 中的上游提交。Redis 扩展只是客户端，本环境没有启动 Redis 或 PostgreSQL 服务。未安装与具体业务/运行方式相关的 Swoole、MongoDB、Oracle、SQL Server、Xdebug 等扩展；扩展齐全也不能突破框架本身的 PHP 版本要求。

## 添加站点

启动后，所有新增虚拟主机共用本机的 80 端口。三个 demo 也支持通过各自的域名访问，直接访问 8001–8003 的方式可继续使用。

1. 将站点放到 html/ 下，例如 html/example.test/。Nginx 和三个 PHP 容器内的路径统一为 /var/www/html/example.test/。
2. 在 nginx/conf.d/ 新建 example.test.conf，监听容器的 80 端口，用 server_name 指定域名。在 fastcgi_pass 填 php56、php74 或 php86。
3. 在访问端的 hosts 文件添加 127.0.0.1 example.test。用 Windows 浏览器访问时编辑 Windows 的 hosts 文件，然后打开 http://example.test/。
4. 执行 docker compose exec nginx nginx -t，成功后执行 docker compose exec nginx nginx -s reload。

三个 demo 的 .conf 可作为普通 PHP 站点的示例。Laravel 等框架使用 public 目录作为 Web 根目录，并且只将公开入口 index.php 转发给 PHP-FPM。例如：

~~~nginx
server {
    listen 80;
    server_name example.test;
    root /var/www/html/example.test/public;
    index index.php;

    location ~ /\. {
        deny all;
    }

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /index.php {
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root/index.php;
        fastcgi_pass php86;
    }

    location ~ \.php(?:/|$) {
        return 404;
    }
}
~~~

也可以先用 curl -H 'Host: example.test' http://127.0.0.1/ 测试。新增站点和虚拟主机由 Git 忽略，Docker 会正常加载本地文件，无需修改 Compose 或重建镜像。

Nginx 只读挂载 html/，三个 PHP 容器共用可读写挂载。PHP-FPM 使用 www-data，只给应用需要写入的目录设置相应权限，例如 Laravel 的 storage 和 bootstrap/cache。此环境面向本地开发，共享同一运行用户的站点可访问该用户有权读取的其他站点文件。


内存限制 256MB，单文件上传限制 32MB，请求体上限 40MB。OPcache 检查代码更新时间，方便本地修改。扩展自带源码编译，软件包源保留签名校验：PHP 5.6 使用 Debian Stretch 官方归档源，PHP 7.4 使用 2026-08-31 的官方 Bullseye 安全源快照，并对旧索引放宽 Valid-Until 检查。这套环境用于本地兼容测试，PHP 5.6/7.4 均已停止官方支持。

## 数据库

每张表只有 id（无符号整数自增主键）、name（VARCHAR(100)）两个字段；首次初始化各插入两条记录，例如 demo1-A、demo1-B。页面实际查询 MySQL，并显示运行时 PHP 版本。

可复制 `.env.example` 为 `.env` 后调整密码；未配置时使用 Compose 中的本地演示默认密码。三个 demo 通过 DEMO_DB_* 环境变量使用普通用户 demo。新增站点在自己的应用配置中连接 mysql:3306，使用自己的数据库和账号。MySQL 不发布宿主机端口。站点端口仅绑定本机回环地址。

MySQL 数据保存在 mysql/data。初始化 SQL 只在空数据目录首次启动时执行，现有数据库不会自动重置或补数据；修改环境变量不会修改现有用户密码。不要删除数据目录来更新已有数据库。为兼容 PHP 5.6 mysqlnd，MySQL 8.0 使用 mysql_native_password。健康检查确认三张表可查询后才启动 PHP，PHP-FPM 端口就绪后才启动 Nginx。Nginx 使用 Docker DNS 动态解析 PHP 服务地址（缓存 5 秒），支持 PHP 容器重建后地址变化。
