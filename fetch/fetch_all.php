<?php

require dirname(__DIR__)."/vendor/autoload.php";
require (__DIR__)."/odie.php";

$base_url = 'http://www.zhihu.com';

$stmt = $pdo->prepare('select q_id from question');
$stmt->execute();
$ids = $stmt->fetchAll(PDO::FETCH_COLUMN);

foreach ($ids as $qid) {
    $url = "$base_url/question/$qid";
    echo "fetch $qid\n";
    list($code, $content) = odie_get($url);
    $username_list = get_username_list($content);

    foreach ($username_list as $username => $nickname) {
        $stmt = $pdo->prepare('INSERT INTO answer (name, nickname) VALUES (?,?) ON DUPLICATE KEY UPDATE id=id');
        if (!$stmt->execute(array($username, $nickname))) {
            print_r($stmt->errorInfo());
        }
    }
}


