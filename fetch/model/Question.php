<?php

namespace model;

class Question
{
    public static function getTable()
    {
        return get_table('question');
    }

    public static function setFetched($qid)
    {
        $q = self::getTable();
        $update = array('has_fetch' => true);
        $where = array('id' => $qid);
        $rs = $q->update($where, array('$set' => $update));
        if (!$rs['ok']) {
            echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
        }
        return $rs;
    }

    public static function saveQuestion($qid, $question, $description)
    {
        $q = self::getTable();
        $update = array('title' => $question, 'description' => $description, 'fetched' => time());
        $where = array('id' => $qid);
        $rs = $q->update($where, array('$set' => $update), array('upsert' => true));
        if (!$rs['ok']) {
            echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
        }
        return $rs;
    }
    
    public static function getIds()
    {
        $c = self::getTable();
        $where = array('has_fetch' => array('$exists' => false));
        $c = $c->find($where)->fields(array('id' => true));
        $ret = array();
        foreach ($c as $v) {
            $ret[] = $v['id'];
        }
        return $ret;
    }
}
