<?php
$p = _get('p') ?: 1;
$limit = 100;
$offset = ($p-1)*100;
$orm = ORM::forTable('answer')
    ->join('question', array('answer.q_id', '=', 'question.id'))
    ->join('user', array('answer.user', '=', 'user.name'))
    ->select('*')
    ->select('answer.id', 'aid')
    ->offset($offset)
    ->limit($limit);
if ($upvote = _get('upvote')) {
    $orm->whereGt('answer.vote', $upvote);
}
if ($kw = _get('kw')) {
    $orm->whereRaw('(question.title like ? or user.nick_name like ?)', array("%$kw%", "%$kw%"));
}
$answers = $orm->findMany();

$style = _get('style', 'normal');

$title = '知乎箱底';

include dirname(__DIR__).'/view/admin.phtml';
