<?php

require __DIR__.'/lib.php';
require __DIR__.'/vendor/autoload.php';

$dsn = 'mysql:dbname=zhihu;host=127.0.0.1';
$user = 'root';
$password = '';

ORM::configure($dsn);
ORM::configure('username', $user);
ORM::configure('password', $password);
ORM::configure('driver_options', array(PDO::MYSQL_ATTR_INIT_COMMAND => 'SET NAMES utf8'));

$arr = explode('?', $_SERVER['REQUEST_URI']);
$uri = $arr[0];
$arr = explode('/', trim($uri, '/'));

$controller = isset($arr[0]) && $arr[0] ? $arr[0] : 'index';
$f = __DIR__."/controller/$controller.php";
if (file_exists($f)) {
    require $f;
} else {
    echo '404 page not found';
    exit();
}
