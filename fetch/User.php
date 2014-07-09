<?php
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
        $where = array('nick_name' => $nickname);
        $rs = $u->update($where, array('$set' => $update), true);
        if (!$rs['ok']) {
            echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
        }
        
        return $rs;
    }

    public static function updateByUserName($username, $args)
    {
        if (empty($args)) {
            return true;
        }
        $u = self::getTable();
        $newdata = array('$set' => $args);
        $rs = $u->update(array("username" => $username), $newdata);
        if (!$rs['ok']) {
            echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
        }
        return $rs;
    }
    public static function getUids()
    {
        $u = self::getTable();
        $c = $u->find();
        var_dump($c);
        return $c;
    }

}
