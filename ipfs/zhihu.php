<?php

function www_zhihu_com($answer_url) {
    global $root;
        
    // todo support article

    // check url
    if (!preg_match('/\d+$/', $answer_url, $m)) {
        echo "not good url\n";
        exit(1);
    }

    // fetch url
    $html = file_get_contents($answer_url);

    // trans css
    $html = preg_replace_callback('/([^"]+\.css)"/', '_fetch_res', $html);

    // make image visible
    $html = preg_replace_callback('/<img src="([^"]+)" ([^>]+) data-actualsrc="([^"]+)">/', '_zhihu_image_replace', $html);

    // todo: video (iframe)

    // trim script or it will cause repeat load problem
    $html = preg_replace('#<script src="https://static.zhihu.com/heifetz/[\-\w\.]+\.js"( async="")?></script>#', '', $html);

    // save
    $id = $m[0];
    $file = "$root/$id.html";
    file_put_contents($file, $html);

    return "$id.html";
}

function _zhihu_image_replace($m) {
    $url = $m[3];
    $new_url = _save_res($url);
    // echo "$url => $new_url\n";
    // $to = "<img src=\"$new_url\" $m[2] data-actualsrc=\"$m[3]\">";
    // echo "$m[0] => $to\n";
    return "<img src=\"$new_url\" $m[2] data-actualsrc=\"$m[3]\">";
}