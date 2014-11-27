<?php

require dirname(__DIR__)."/vendor/autoload.php";
require (__DIR__)."/odie.php";
require (__DIR__)."/logic.php";
require (__DIR__)."/db_init.php";

$base_url = 'http://zhihuarchive.duapp.com/upload';

$table = [
    'user' => 'select id, name, nick_name,avatar from user',
    'answer' => 'select id, q_id, user,text, vote from answer where vote > 9',
    'question' => 'select id, title, description from question',
];
foreach ($table as $type => $sql) {
    $stmt = $pdo->prepare($sql);
    if (!$stmt->execute()) {
        print_r($stmt->errorInfo());
    }
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo count($rows),"\n";

    foreach ($rows as $o) {
        $ch = curl_init($base_url);
        $post = http_build_query(['type' => $type, 'data' => $o]);
        echo $post,"\n";
        curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $ret = curl_exec($ch);
        $info = curl_getinfo($ch);
        print_r($info);
        echo "$ret";
    }
}
