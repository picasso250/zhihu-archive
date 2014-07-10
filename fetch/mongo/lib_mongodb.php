<?php

function get_collection()
{
    static $collection;
    if ($collection === null) {
        $m = new MongoClient(); // connect
        $collection = $m->zhihu;
    }
    return $collection;
}

function get_table($table)
{
    $db = get_collection();
    return $db->{$table};
}

function slog($msg)
{
    return error_log(date('Y-m-d H:i:s')." $msg\n", 3, __DIR__.'/fetch.log');
}

function uget($url, $opts = null)
{
    $rs = odie_get($url, $opts);
    slog("$url [$rs[0]]");
    return $rs;
}
