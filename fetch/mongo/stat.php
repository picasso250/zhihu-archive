<?php

require dirname(dirname(__DIR__))."/vendor/autoload.php";
require dirname(__DIR__)."/odie.php";
require dirname(__DIR__)."/logic.php";
require (__DIR__)."/lib_mongodb.php";
require (__DIR__)."/autoload.php";


while (1) {
    $c = get_table('user');
    $user_count = $c->find()->count();

    $c = get_table('question');
    $question_count = $c->find()->count();

    $c = get_table('answer');
    $answer_count = $c->find()->count();
    if (isset($argv[1]) && $argv[1] === '-f') {
        echo "\r";
        echo "$user_count users\t$question_count questions\t$answer_count answers";
        sleep(1);
    } else {
        echo "there are $user_count users\n";
        echo "there are $question_count questions\n";
        echo "there are $answer_count answers\n";
        break;
    }
}
