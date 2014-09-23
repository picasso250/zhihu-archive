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
echo "there are ",count($ids)," questions to fetch\n";

$sum = $existing_sum = 1;
foreach ($ids as $qid) {
    $url = "$base_url/question/$qid";
    timer();
    list($code, $content) = odie_get($url);
    slog($url." [$code]");
    $t = timer();
    echo "Fetch question $qid [$code] $t ms\n";
    $username_list = get_username_list($content);

    timer();
    foreach ($username_list as $username => $nickname) {
        echo "\t$username";
        if (User::saveUser($username, $nickname)) {
            $existing_sum++;
        }
        $sum++;
    }
    Question::setFetched($qid);
    $rate = intval((1 - $existing_sum/$sum) * 100);
    $t = timer();
    echo "\tSave: $t ms\t Rate $rate%\n";
}


