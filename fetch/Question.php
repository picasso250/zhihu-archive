<?php

class Question
{
    public static function getTable()
    {
        return get_table('question');
    }
    public static function getIds()
    {
        $c = self::getTable();
        $c = $c->find();
        var_dump($c);
        return $c;
    }
}
