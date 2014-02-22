<?php

require dirname(__DIR__)."/vendor/autoload.php";
require (__DIR__)."/odie.php";
require (__DIR__)."/logic.php";
require (__DIR__)."/db_init.php";

$base_url = 'http://www.zhihu.com';

$stmt = $pdo->prepare('select id from question');
if (!$stmt->execute()) {
    print_r($stmt->errorInfo());
}
$ids = $stmt->fetchAll(PDO::FETCH_COLUMN);

foreach ($ids as $qid) {
    $url = "$base_url/question/$qid";
    echo "fetch $qid\n";
    list($code, $content) = odie_get($url);
    $username_list = get_username_list($content);

    foreach ($username_list as $username => $nickname) {
        echo "\t$username ==> $nickname\n";
        $stmt = $pdo->prepare('INSERT INTO user (name, nick_name) VALUES (?,?) ON DUPLICATE KEY UPDATE nick_name=?');
        if (!$stmt->execute(array($username, $nickname, $nickname))) {
            print_r($stmt->errorInfo());
        }
    }
}


