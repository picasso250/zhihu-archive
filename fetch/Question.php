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
        $c = $c->find()->fields(array('id' => true));
        $ret = array();
        foreach ($c as $v) {
            $ret[] = $v['id'];
        }
        return $ret;
    }
}
