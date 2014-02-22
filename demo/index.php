<?php

require __DIR__.'/lib.php';
require dirname(__DIR__).'/vendor/autoload.php';

$dsn = 'mysql:dbname=zhihu;host=127.0.0.1';
$user = 'root';
$password = '';

ORM::configure($dsn);
ORM::configure('username', $user);
ORM::configure('password', $password);
ORM::configure('driver_options', array(PDO::MYSQL_ATTR_INIT_COMMAND => 'SET NAMES utf8'));

$answers = ORM::forTable('answer')
    ->join('question', array('answer.q_id', '=', 'question.id'))
    ->join('user', array('answer.user', '=', 'user.name'))
    ->limit(10)
    ->findMany();

$style = _get('style', 'normal');

include __DIR__.'/index.phtml';
