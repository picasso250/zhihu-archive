<?php

function odie_get($url, $opts = null) {
    $tmp = __DIR__.'/cache';
    if (is_dir($tmp)) {
        $filename = $tmp.'/'.urlencode($url);
        if (file_exists($filename)) {
            return array(200, file_get_contents($filename));
        }
    }

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $content = curl_exec($ch);
    if ($errno = curl_errno($ch)) {
        return array($errno, curl_error($ch));
    }
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    if (is_dir($tmp) && $code == 200) {
        file_put_contents($filename, $content);
    }
    return array($code, $content);
}
