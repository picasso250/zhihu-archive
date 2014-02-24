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

$orm = ORM::forTable('answer')
    ->join('question', array('answer.q_id', '=', 'question.id'))
    ->join('user', array('answer.user', '=', 'user.name'))
    ->select('*')
    ->select('answer.id', 'aid')
        ->whereGt('answer.vote', 1000)
    ->limit(10);
if ($kw = _get('kw')) {
    $orm->whereRaw('(question.title like ? or user.nick_name like ?)', array("%$kw%", "%$kw%"));
}
$answers = $orm->findMany();

$style = _get('style', 'normal');

$title = '知乎箱底';

include __DIR__.'/index.phtml';
