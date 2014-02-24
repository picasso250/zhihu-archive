<?php

function save_answer($base_url, $username, $answer_link_list) {
    foreach ($answer_link_list as $url) {
        $url = $base_url.$url;
        list($_, $content) = odie_get($url);
        list($question, $content) = parse_answer($content);
        echo "\t$question\n";
        $content = '<link rel="stylesheet" href="http://static.zhihu.com/static/ver/f004e446ca569e4897e59cf26da3e2dc.z.css" type="text/css" media="screen,print" />'
            .$content
            .'<div><a href="'.$url.'">原链接</a></div>'
            .'<script src="http://code.jquery.com/jquery-1.11.0.min.js"></script>'
            .'<script>$("img").each(function(){$(this).attr("src",$(this).attr("data-actualsrc"))});</script>'
            ;
        $root = __DIR__."/$username";
        if (!is_dir($root)) {
            mkdir($root);
        }
        $question = mb_strimwidth($question, 0, 40, '...', 'utf8');
        $question = str_replace('/', '-', $question);
        file_put_contents("$root/$question.html", $content);
    }
}

function parse_answer($content) {
    $dom = HTML5::loadHTML($content);
    $answer = $dom->getElementById('zh-question-answer-wrap');
    $answer = ($answer->C14N());
    $q = $dom->getElementById('zh-question-title');
    $a = $q->getElementsByTagName('a')->item(0);
    $question = $a->textContent;
    return array($question, $answer);
}

function parse_answer_pure($content) {
    $dom = HTML5::loadHTML($content);
    $answer = $dom->getElementById('zh-question-answer-wrap');
    if (empty($answer)) {
        file_put_contents('last_error.html', $content);
    }
    foreach ($answer->getElementsByTagName('div') as $div) {
        if ($class = $div->getAttribute('class')) {
            $class = explode(' ', $class);
            if (in_array('zm-editable-content', $class)) {
                $answer = $div->C14N();
            }
        }
    }
    
    $q = $dom->getElementById('zh-question-title');
    $a = $q->getElementsByTagName('a')->item(0);
    $question = $a->textContent;
    
    $descript = $dom->getElementById('zh-question-detail');
    $descript = $descript->getElementsByTagName('div')->item(0)->C14N();
    
    return array($question, $descript, $answer);
}

function get_answer_link_list($content) {
    $dom = HTML5::loadHTML($content);
    $dom = $dom->getElementById('zh-profile-answer-list');
    $ret = array();
    foreach ($dom->getElementsByTagName('a') as $key => $node) {
        if ($attr = $node->getAttribute('class') == 'question_link') {
            $ret[] = ($node->getAttribute('href'));
        }
    }
    return $ret;
}

function get_page_num($content) {
    $rs = preg_match_all('%<a href="\?page=(\d+)%', $content, $matches);
    if (!$rs) {
        return 1;
    }
    return (int) max($matches[1]);
}

function get_username_list($content) {
    $dom = HTML5::loadHTML($content);
    $ret = array();
    foreach ($dom->getElementsByTagName('a') as $key => $node) {
        $href = $node->getAttribute('href');
        if (preg_match('%/people/(.+)$%', $href, $matches)) {
            $username = $matches[1];
            $ret[$username] = $node->textContent;
        }
    }
    return ($ret);
}

function save_answer_to_db($base_url, $username, $answer_link_list) {
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
        list($question, $descript, $content) = parse_answer_pure($content);
        echo "\t$question\n";
        $stmt = $pdo->prepare('INSERT INTO question (id, title, description) VALUES (?,?,?) ON DUPLICATE KEY UPDATE title=?,description=?');
        if (!$stmt->execute(array($qid, $question, $descript, $question, $descript))) {
            print_r($stmt->errorInfo());
        }

        $stmt = $pdo->prepare('INSERT INTO answer (id, q_id, user, text) VALUES (?,?,?,?) ON DUPLICATE KEY UPDATE text=?');
        if (!$stmt->execute(array($aid, $qid, $username, $content, $content))) {
            print_r($stmt->errorInfo());
        }
    }
}
