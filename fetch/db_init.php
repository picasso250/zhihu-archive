<?php
$dsn = 'mysql:dbname=zhihu;host=127.0.0.1';
$user = 'root';
$password = '';

try {
    $pdo = new PDO($dsn, $user, $password, array(PDO::MYSQL_ATTR_INIT_COMMAND => 'SET NAMES \'UTF8\''));
} catch (PDOException $e) {
    echo 'Connection failed: ' . $e->getMessage();
    exit();
}
