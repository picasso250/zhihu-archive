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
    $t = $db->{$table};
    switch ($table) {
        case 'answer':
            $t->ensureIndex(array('vote' => 1, 'q_id' => 1,));
            break;
        
        default:
            # code...
            break;
    }
    return $t;
}

function slog($msg)
{
    $f = __DIR__.'/'.date('Ymd').'.log';
    return error_log(date('Y-m-d H:i:s')." $msg\n", 3, $f);
}

function uget($url, $opts = null)
{
    $rs = odie_get($url, $opts);
    slog("$url [$rs[0]]");
    return $rs;
}
