<?php

require dirname(dirname(__DIR__))."/vendor/autoload.php";
require dirname(__DIR__)."/odie.php";
require dirname(__DIR__)."/logic.php";
require (__DIR__)."/lib_mongodb.php";
require (__DIR__)."/autoload.php";

use model\User;
use model\Question;
use model\Answer;

$base_url = 'http://www.zhihu.com';

$count = User::getNotFetchedUserCount();
echo "there are $count user to fetch\n";
$n = 0;
while ($username = User::getNotFetchedUserName($n)) {
    User::updateByUserName($username, array('fetching' => 1));
    $n++;
    $url = "$base_url/people/$username/answers";
    echo "\nfetch No.$n $username\t";
    timer();
    list($code, $content) = uget($url);
    $t = timer();
    $avg = intval(get_average($t, 'user page'));
    echo "[$code]\t$t ms\tAvg: $avg ms\n";
    if ($code == 404) {
        slog("user $username fetch fail, code $code");
        User::updateByUserName($username, array('has_fetch' => true, 'fetch_fail' => true));
        echo "没有这个用户 $username\n";
        continue;
    }
    if ($code != 200) {
        slog("user $username fetch fail, code $code");
        User::updateByUserName($username, array('has_fetch' => true, 'fetch_fail' => true));
        echo "奇奇怪怪的返回码 $code\n";
        continue;
    }
    
    $dom = HTML5::loadHTML($content);
    $dom = $dom->getElementById('zh-pm-page-wrap');
    foreach ($dom->getElementsByTagName('img') as $key => $node) {
        if (($attr = $node->getAttribute('class')) == 'zm-profile-header-img zg-avatar-big zm-avatar-editor-preview') {
            $src = ($node->getAttribute('src'));
        }
    }
    
    User::updateByUserName($username, array('avatar' => $src));

    $link_list = get_answer_link_list($content);
    $rs = Answer::saveAnswer($base_url, $username, $link_list);

    $num = get_page_num($content);
    if ($num > 1) {
        foreach (range(2, $num) as $i) {
            echo "\nNo. $n fetch page $i\t";
            $url_page = "$url?page=$i";
            timer();
            list($code, $content) = uget($url_page);
            $t = timer();
            $avg = intval(get_average($t, 'user page'));
            slog("$url_page [$code]");
            echo "[$code]\t$t ms\tAvg: $avg ms\n";
            if ($code != 200) {
                echo "奇奇怪怪的返回码 $code\n";
                continue;
            }
            $link_list = get_answer_link_list($content);
            Answer::saveAnswer($base_url, $username, $link_list);
        }
    }
    User::updateByUserName($username, array('has_fetch' => true));
}
