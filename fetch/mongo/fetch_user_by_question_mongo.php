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

$ids = Question::getIds();

foreach ($ids as $qid) {
    $url = "$base_url/question/$qid";
    echo "fetch $qid\n";
    list($code, $content) = odie_get($url);
    $username_list = get_username_list($content);

    foreach ($username_list as $username => $nickname) {
        echo "\t$username\t==> $nickname\n";
        User::saveUser($username, $nickname);
    }
    Question::setFetched($qid);
}


