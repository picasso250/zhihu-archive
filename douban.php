<?php

function book_douban_com($url) {
    return movie_douban_com($url);
}
function movie_douban_com($url) {
    global $root;
        
    // todo support music?

    // check url of movie
    if (!preg_match('/(\d+)\/$/', $url, $m)) {
        echo "not good url\n";
        exit(1);
    }

    // fetch url
    $html = file_get_contents($url);

    // trans css
    $html = preg_replace_callback('/"([^"]+\.css)"/', '_fetch_res', $html);

    // make image visible (solve 403 problem)
    $html = preg_replace_callback('/<(img(?: [^>]+)?) src="([^"]+)" ([^>]+)\/>/', '_douban_image_replace', $html);
    $html = preg_replace_callback('/<img ([^>]+) src="([^"]+)"/', '_image_local', $html);

    // save
    $id = $m[1];
    $file = "$root/$id.html";
    file_put_contents($file, $html);

    return "$id.html";
}

function _douban_image_replace($m) {
    // echo "$m[0]\n";
    $url = $m[2];
    if (strpos($url, 'https')!==0){
        return $m[0];
    }
    $new_url = _save_res($url);
    return "<img $m[1] src=\"$new_url\" $m[3]\/>";
}