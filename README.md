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

## 框架目录与配置

Nginx 只读挂载站点，PHP 各自可读写对应站点，方便框架写入缓存、日志和上传内容。容器内 PHP-FPM 使用 www-data；部署框架时只需给其实际的 storage、runtime、cache、uploads 等可写目录设置适当权限，不要把整个项目设置为 777。当前演示目录的根入口为 index.php；Laravel/Symfony 等框架需要按项目结构将 Nginx root 改为对应 public 目录。

修改 Nginx 配置后执行 `docker compose exec nginx nginx -t`，确认无误再执行 `docker compose exec nginx nginx -s reload`；容器重建后 DNS 刷新可能有数秒短暂过渡。

内存限制 256MB，单文件上传限制 32MB，请求体上限 40MB。OPcache 检查代码更新时间，方便本地修改。扩展自带源码编译，软件包源保留签名校验：PHP 5.6 使用 Debian Stretch 官方归档源，PHP 7.4 使用 2026-08-31 的官方 Bullseye 安全源快照，并对旧索引放宽 Valid-Until 检查。这套环境用于本地兼容测试，PHP 5.6/7.4 均已停止官方支持。

## 数据库

每张表只有 id（无符号整数自增主键）、name（VARCHAR(100)）两个字段；首次初始化各插入两条记录，例如 demo1-A、demo1-B。页面实际查询 MySQL，并显示运行时 PHP 版本。

可复制 `.env.example` 为 `.env` 后调整密码；未配置时使用 Compose 中的本地演示默认密码。PHP 使用普通用户 demo，数据库不发布宿主机端口。站点端口仅绑定本机回环地址。

MySQL 数据保存在 mysql/data。初始化 SQL 只在空数据目录首次启动时执行，现有数据库不会自动重置或补数据；修改环境变量不会修改现有用户密码。不要删除数据目录来更新已有数据库。为兼容 PHP 5.6 mysqlnd，MySQL 8.0 使用 mysql_native_password。健康检查确认三张表可查询后才启动 PHP，PHP-FPM 端口就绪后才启动 Nginx。Nginx 使用 Docker DNS 动态解析 PHP 服务地址（缓存 5 秒），支持 PHP 容器重建后地址变化。
