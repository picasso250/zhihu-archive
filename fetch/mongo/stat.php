<?php

require dirname(dirname(__DIR__))."/vendor/autoload.php";
require dirname(__DIR__)."/odie.php";
require dirname(__DIR__)."/logic.php";
require (__DIR__)."/lib_mongodb.php";
require (__DIR__)."/autoload.php";

$c = get_table('user');
$c = $c->find()->count();
echo "there are $c users\n";

$c = get_table('question');
$c = $c->find()->count();
echo "there are $c questions\n";

$c = get_table('answer');
$c = $c->find()->count();
echo "there are $c answers\n";
