<?php

require __DIR__.'/lib.php';
require __DIR__.'/vendor/autoload.php';

$map = ['answer', 'question', 'user'];
$n = count($map) - 1;
$url = 'http://3.xctest.sinaapp.com/upload';
while (1) {
    $i = rand(0, $n);
    $type = $map[$i];
    $entry = ORM::forTable($type)->where('is_upload', 0)->findOne();

    $data = ['type' => $type, 'data' => $entry->toArray()];

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    $content = curl_exec($ch);
    $response = json_decode($content, true);
    if (json_last_error()) {
        app_log('error: json decode error %s', json_last_error());
        throw new Exception("json decode error", 1);
    }
    if (empty($response)) {
        app_log('error: response empty');
        throw new Exception("response empty", 1);
    }
    if ($response['code'] !== 0) {
        app_log('error: response code %s message %s', $response['code'], $response['message']);
        throw new Exception("response code ".$response['code'], 1);
    }
    $entry->is_upload = 1;
    $entry->save();
    app_log('curl %s of type %s with %s', $url, $type, json_encode($entry->toArray()));
    sleep(2);
}
