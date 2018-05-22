<?php

require "zhihu.php";
require "douban.php";

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

// see call which
$url = $argv[1];
$a = parse_url($url);
if (!isset($a['host'])) {
    echo "Please give me a url\n";
    exit(1);
}
$host = $a['host'];
$func = str_replace('.', '_', $host);
if (!function_exists($func)) {
    echo "$host not support\n";
    exit(1);
}
$name = $func($url);

// add to ipfs
// todo check ipfs exists
$cmd = "ipfs add -r $root";
echo "$cmd\n";
$ret = exec($cmd);
$a = explode(' ', $ret);
echo "http://localhost:8080/ipfs/$a[1]/$name\n";
echo "https://ipfs.io/ipfs/$a[1]/$name\n";

// == lib ==

function _fetch_res($m) {
    global $root;
    $url = $m[1];
    if ($url[0]=='/'&&$url[1]=='/')
        $url = 'https:'.$url;
    return _save_res($url).'"';
}

function _save_res($url) {
    global $root;
    $a = parse_url($url);
    $file = $root.$a['path'];
    if (!is_file($file)) {
        echo "fetch $url\n";
        $content = file_get_contents($url);
        $dir = dirname($file);
        if (!is_dir($dir)) mkdir($dir, 0777, true);
        file_put_contents($file, $content);
    }
    return substr($a['path'],1);
}
function _image_local($m) {
    $url = $m[2];
    $new_url = _save_res($url);
    return "<img $m[1] src=\"$new_url\"";
}