<?php

$id = _post('id');
if (isset($_SERVER['HTTP_APPNAME'])) {
    $answer = ORM::forTable('answer')->findOne($id);
    if ($answer) {
        echo json_encode(array('code' => 1, 'msg' => 'has answer', 'data' => $answer->asArray()));
    } else {
        $answer = ORM::forTable('answer')->create();
        $question = ORM::forTable('question')->create();
        $user = ORM::forTable('user')->create();
        $answer->set($_POST['answer']);
        $answer->save();
        $question->set($_POST['question']);
        $question->save();
        $user->set($_POST['user']);
        $user->save();
        echo json_encode(array('code' => 0, 'msg' => 'ok', 'data' => $answer->asArray()));
    }
} else {
    $answer = ORM::forTable('answer')->findOne($id);
    $question = ORM::forTable('question')->findOne($answer->q_id);
    $user = ORM::forTable('user')->findOne($answer->user);

    $data = compact('id', 'answer', 'question', 'user');

    $url = 'http://3.xctest.sinaapp.com/upload';
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    $content = curl_exec($ch);
}
