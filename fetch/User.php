<?php
// logic of mongodb
class User
{
    public static function getTable()
    {
        return get_table('user');
    }
    public static function updateByUserName($username, $args)
    {
        if (empty($args)) {
            return true;
        }
        $u = self::getTable();
        $newdata = array('$set' => $args);
        $rs = $u->update(array("username" => $username), $newdata);
        var_dump($rs);
        return $rs;
    }
    public static function getUids()
    {
        $u = self::getTable();
        $c = $u->find();
        var_dump($c);
        return $c;
    }

    public function save_answer_to_db($base_url, $username, $answer_link_list) {
        global $pdo;
        foreach ($answer_link_list as $url) {
            echo "\t{$base_url}$url";
            if (preg_match('%^/question/(\d+)/answer/(\d+)%', $url, $matches)) {
                $qid = $matches[1];
                $aid = $matches[2];
            } else {
                echo "$url not good\n";
                exit(1);
            }
            $url = $base_url.$url;
            list($code, $content) = odie_get($url);
            echo "\t$code\n";
            // 自动重刷
            $i = 0;
            while ($code != 200) {
                list($code, $content) = odie_get($url);
                echo "\t$code\n";
                if ($i > 5) {
                    echo 'can not fetch',"\n";
                    return false;
                }
                $i++;
            }
            if (empty($content)) {
                echo "content is empty\n";
                return false;
            }
            list($question, $descript, $content, $vote) = parse_answer_pure($content);
            echo "\t^$vote\t$question\n";
            $stmt = $pdo->prepare('INSERT INTO question (id, title, description) VALUES (?,?,?) ON DUPLICATE KEY UPDATE title=?,description=?');
            if (!$stmt->execute(array($qid, $question, $descript, $question, $descript))) {
                print_r($stmt->errorInfo());
            }

            $stmt = $pdo->prepare('INSERT INTO answer (id, q_id, user, text, vote) VALUES (?,?,?,?,?) ON DUPLICATE KEY UPDATE text=?, vote=?');
            if (!$stmt->execute(array($aid, $qid, $username, $content, $vote, $content, $vote))) {
                print_r($stmt->errorInfo());
            }
        }
    }

}
