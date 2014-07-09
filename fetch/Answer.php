<?php

class Answer
{
    public static function saveAnswer($base_url, $username, $answer_link_list) {
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

            $q = get_table('question');
            $update = array('title' => $question, 'description' => $descript);
            $where = array('id' => $qid, 'title' => $question, 'description' => $descript);
            $rs = $q->update($where, array('$set' => $update), array('upsert' => true));
            if (!$rs['ok']) {
                echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
            }

            $a = get_table('answer');
            $update = array('id' => $aid, 'q_id' => $qid, 'user' => $username, 'text' => $content, 'vote' => $vote);
            $where = array('text' => $content, 'vote' => $vote);
            $rs = $a->update($where, array('$set' => $update), array('upsert' => true));
            if (!$rs['ok']) {
                echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
            }
        }
    }
}
