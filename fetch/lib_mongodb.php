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
