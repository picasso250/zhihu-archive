<?php

namespace model;

class Answer
{
    public static function _saveAnswer($aid, $qid, $username, $content, $vote) {
        $a = get_table('answer');
        $update = array('id' => $aid, 'q_id' => $qid, 'user' => $username, 'text' => $content, 'vote' => $vote, 'fetched' => time());
        $where = array('id' => $aid);
        $rs = $a->update($where, array('$set' => $update), array('upsert' => true));
        if (!$rs['ok']) {
            echo basename(__FILE__).':'.__LINE__.' '.$rs['err']."\n";
        }
        return $rs;
    }

    public static function saveAnswer($base_url, $username, $answer_link_list) {
        foreach ($answer_link_list as $url) {
            if (preg_match('%^/question/(\d+)/answer/(\d+)%', $url, $matches)) {
                $qid = $matches[1];
                $aid = $matches[2];
            } else {
                echo "$url not good\n";
                exit(1);
            }
            $url = $base_url.$url;
            echo "\r$url";
            $t = microtime(true);
            list($code, $content) = odie_get($url);
            if ($code != 200) { // fail fast
                slog("$url [$code] error");
                return false;
            }
            echo "\t[$code]";
            $t = intval((microtime(true) - $t) * 1000);
            echo "\t$t ms";
            if (empty($content)) {
                echo "content is empty\n";
                slog("$url [$code] empty");
                return false;
            }
            list($question, $descript, $content, $vote) = parse_answer_pure($content);
            slog("$url [$code] ^$vote\t$question");

            Question::saveQuestion($qid, $question, $descript);

            Answer::_saveAnswer($aid, $qid, $username, $content, $vote);
        }
    }
}
