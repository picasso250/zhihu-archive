<?php
require dirname(dirname(__DIR__))."/vendor/autoload.php";
require dirname(__DIR__)."/odie.php";
require dirname(__DIR__)."/logic.php";
require (__DIR__)."/lib_mongodb.php";
require (__DIR__)."/autoload.php";

$q = get_table('question');
$a = get_table('answer');
$questions = $q->find()->limit(1000);
$i = 0;
foreach ($questions as $q) {
    $where = array('q_id' => $q['id'], 'vote' => array('$gt' => 20));
    $answers = $a->find($where)->limit(3);
    if ($answers->count()) {
        $data[] = array(
            'question' => $q,
            'answers' => $answers,
        );
        $i++;
        if ($i > 10) {
            break;
        }
    }
}
include __DIR__.'/index.phtml';
