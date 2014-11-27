<?php

$type = _post('type');
$data = _post('data');
app_log('recieve type %s with %s', $type, json_encode($data));
$entry = ORM::forTable($type)->findOne($data['id']);
if ($entry) {
    $code = 1;
    $message = 'has entry';
} else {
    $entry = ORM::forTable('entry')->create();
    $code = 0;
    $message = 'ok';
}
$entry->set($data);
$entry->save();
echo json_encode(array('code' => $code, 'message' => $message));
app_log('recieve type %s with %s', $type, json_encode($data));
