<?php

require dirname(__DIR__)."/vendor/autoload.php";
require (__DIR__)."/odie.php";
require (__DIR__)."/logic.php";
require (__DIR__)."/db_init.php";

$base_url = 'http://www.zhihu.com';

$stmt = $pdo->prepare('select name from user');
if (!$stmt->execute()) {
    print_r($stmt->errorInfo());
}
$uids = $stmt->fetchAll(PDO::FETCH_COLUMN);

foreach ($uids as $username) {
    $url = "$base_url/people/$username/answers";
    echo "fetch $username\n";
    list($code, $content) = odie_get($url);
    if ($code == 404) {
        echo "没有这个用户 $username\n";
        continue;
    }
    
    $dom = HTML5::loadHTML($content);
    $dom = $dom->getElementById('zh-pm-page-wrap');
    foreach ($dom->getElementsByTagName('img') as $key => $node) {
        if (($attr = $node->getAttribute('class')) == 'zm-profile-header-img zg-avatar-big zm-avatar-editor-preview') {
            $src = ($node->getAttribute('src'));
        }
    }
    
    $stmt = $pdo->prepare('update question set avatar=? where name=?');
    if (!$stmt->execute(array($src, $username))) {
        print_r($stmt->errorInfo());
    }

    $link_list = get_answer_link_list($content);
    $rs = save_answer_to_db($base_url, $username, $link_list);

    $num = get_page_num($content);
    if ($num > 1) {
        foreach (range(2, $num) as $i) {
            echo "fetch page $i\t";
            $url_page = "$url?page=$i";
            list($code, $content) = odie_get($url_page);
            echo "$code\n";
            $link_list = get_answer_link_list($content);
            save_answer_to_db($base_url, $username, $link_list);
        }
    }
}
