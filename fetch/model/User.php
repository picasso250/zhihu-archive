<?php

namespace model;

// logic of mongodb
class User
{
    public static function getTable()
    {
        return get_table('user');
    }

    public static function saveUser($username, $nickname)
    {
        $u = self::getTable();
        $update = array('name' => $username, 'nick_name' => $nickname);
        $where = array('name' => $username);
        $rs = $u->update($where, array('$set' => $update), array('upsert' => true));
        if ($rs['updatedExisting']) {
            echo "\tupdatedExisting";
        }
        echo "\n";
        if (!$rs['ok']) {
            echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
        }
        
        return $rs['updatedExisting'];
    }

    public static function getNotFetchedUserCount()
    {
        $u = self::getTable();
        $where = array(
            'has_fetch' => array('$exists' => false),
            'name' => array('$exists' => true),
        );
        $c = $u->find($where)->count();
        return $c;
    }
    
    public static function getNotFetchedUserName($i = 1, $argv = null)
    {
        if ($i == 0 && isset($argv[1])) {
            echo "you say $argv[1]\n";
            return $argv[1];
        }
        $u = self::getTable();
        $where = array(
            'has_fetch' => array('$exists' => false),
            'fetching' => array('$exists' => false),
            'name' => array('$exists' => true),
        );
        $c = $u->find($where)->fields(array('name' => true))->limit(1);
        foreach ($c as $v) {
            return $v['name'];
        }
        return false;
    }
    public static function updateByUserName($username, $args)
    {
        if (empty($args)) {
            return true;
        }
        $u = self::getTable();
        $newdata = array('$set' => $args);
        $rs = $u->update(array("name" => $username), $newdata, array('upsert' => true));
        if (!$rs['ok']) {
            echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
        }
        return $rs;
    }
    
    public static function getUids()
    {
        $u = self::getTable();
        $where = array(
            'has_fetch' => array('$exists' => false),
            'name' => array('$exists' => true),
        );
        $c = $u->find($where)->fields(array('name' => true));
        $ret = array();
        foreach ($c as $v) {
            $ret[] = $v['name'];
        }
        return $ret;
    }

}
