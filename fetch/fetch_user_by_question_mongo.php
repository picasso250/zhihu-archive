<?php

require dirname(__DIR__)."/vendor/autoload.php";
require (__DIR__)."/odie.php";
require (__DIR__)."/logic.php";
require (__DIR__)."/db_init.php";
require (__DIR__)."/lib_mongodb.php";
require (__DIR__)."/Question.php";
require (__DIR__)."/Answer.php";
require (__DIR__)."/User.php";

$base_url = 'http://www.zhihu.com';

$ids = Question::getIds();

foreach ($ids as $qid) {
    $url = "$base_url/question/$qid";
    echo "fetch $qid\n";
    list($code, $content) = odie_get($url);
    $username_list = get_username_list($content);

    foreach ($username_list as $username => $nickname) {
        echo "\t$username ==> $nickname\n";
        User::saveUser($username, $nickname);
        
    }
}


