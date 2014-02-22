<?php

require dirname(__DIR__)."/vendor/autoload.php";
require (__DIR__)."/odie.php";
require (__DIR__)."/logic.php";

$base_url = 'http://www.zhihu.com';
$qid = '22023880';
$url = "$base_url/question/$qid";
echo "fetch $qid\n";
list($code, $content) = odie_get($url);
$username_list = get_username_list($content);
var_dump($username_list);


