<?php

// check param
if (!isset($argv[1])) {
    echo "Usage: $argv[0] answer_url\n";
    exit();
}

// check data dir
$root = 'data';
if (!is_dir($root)) {
    echo "No dir data\n";
    exit(1);
}

// check url
$answer_url = $argv[1];
if (!preg_match('/\d+$/', $answer_url, $m)) {
    echo "not good url\n";
    exit(1);
}

// fetch url
$html = file_get_contents($answer_url);

// trans css
$html = preg_replace_callback('/([^"]+\.css)"/', 'fetch_css', $html);

// trim script or it will cause repeat load problem
$html = preg_replace('#<script src="https://static.zhihu.com/heifetz/[\-\w\.]+\.js"( async="")?></script>#', '', $html);

// save
$id = $m[0];
$file = "$root/$id.html";
file_put_contents($file, $html);

// add to ipfs
$ret = exec("ipfs add -r data");
$a = explode(' ', $ret);
echo "http://localhost:8080/ipfs/$a[1]/$id.html\n";
echo "https://ipfs.io/ipfs/$a[1]/$id.html\n";

function fetch_css($m) {
    global $root;
    $url = $m[1];
    $a = parse_url($url);
    $file = $root.$a['path'];
    if (!is_file($file)) {
        echo "fetch $url\n";
        $content = file_get_contents($url);
        $dir = dirname($file);
        if (!is_dir($dir)) mkdir($dir, 0777, true);
        file_put_contents($file, $content);
    }
    return substr($a['path'],1).'"';
}