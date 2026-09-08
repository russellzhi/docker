<?php
header('Content-Type: text/html; charset=utf-8');
$table = 'demo2';
$rows = array();
$error = false;
try {
    $pdo = new PDO(
        'mysql:host=' . getenv('DB_HOST') . ';dbname=' . getenv('DB_NAME') . ';charset=utf8mb4',
        getenv('DB_USER'),
        getenv('DB_PASSWORD'),
        array(PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC)
    );
    $rows = $pdo->query('SELECT id, name FROM demo2 ORDER BY id')->fetchAll();
} catch (Exception $e) {
    http_response_code(503);
    error_log($e->getMessage());
    $error = true;
}
function escape($value) {
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}
?>
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Demo2 · 数据查询</title>
    <style>
        body { font: 16px/1.6 system-ui, sans-serif; background: #f4f6fa; color: #243047; margin: 0; padding: 40px 20px; }
        main { max-width: 760px; margin: auto; padding: 28px; background: white; border-radius: 12px; }
        h1 { margin-top: 0; } p { color: #526078; }
        table { width: 100%; border-collapse: collapse; text-align: left; }
        caption { text-align: left; margin-bottom: 12px; font-weight: 600; }
        th, td { padding: 12px 16px; border-bottom: 1px solid #e2e8f0; }
        th { background: #edf2fa; } .error { color: #b42318; }
    </style>
</head>
<body><main>
    <h1>Demo2</h1>
    <p>PHP <?= escape(PHP_VERSION) ?> · 数据库 demo · 表 <?= escape($table) ?></p>
    <?php if ($error): ?>
        <p class="error" role="alert">数据库暂时不可用，请稍后重试。</p>
    <?php else: ?>
        <table>
            <caption><?= escape($table) ?> 查询结果</caption>
            <thead><tr><th scope="col">id</th><th scope="col">name</th></tr></thead>
            <tbody>
            <?php foreach ($rows as $row): ?>
                <tr><td><?= escape($row['id']) ?></td><td><?= escape($row['name']) ?></td></tr>
            <?php endforeach; ?>
            <?php if (!$rows): ?><tr><td colspan="2">暂无数据</td></tr><?php endif; ?>
            </tbody>
        </table>
    <?php endif; ?>
</main></body>
</html>
