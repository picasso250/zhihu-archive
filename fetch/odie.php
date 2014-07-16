<?php

function odie_get($url, $opts = null) {
    $tmp = __DIR__.'/cache';
    $has_dir = is_dir($tmp);
    if ($has_dir) {
        $filename = $tmp.'/'.urlencode($url);
        if (file_exists($filename)) {
            return array(200, file_get_contents($filename));
        }
    }

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10); // wait
    curl_setopt($ch, CURLOPT_DNS_CACHE_TIMEOUT, 1200); // cache dns 20 minutes
    $content = curl_exec($ch);
    if ($errno = curl_errno($ch)) {
        return array($errno, curl_error($ch));
    }
    $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    
    if ($has_dir && $code == 200) {
        file_put_contents($filename, $content);
    }
    return array($code, $content);
}
