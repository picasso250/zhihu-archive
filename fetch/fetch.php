<?php

require dirname(__DIR__)."/vendor/autoload.php";

$username = 'liuniandate';
$base_url = 'http://www.zhihu.com';
$url = "$base_url/people/$username/answers";
echo "fetch $username\n";
list($_, $content) = get($url);
$link_list = get_answer_link_list($content);
save_answer($base_url, $link_list);

$num = get_page_num($content);
if ($num > 1) {
    foreach (range(2, $num) as $i) {
        echo "fetch page $i\n";
        $url_page = "$url?page=$i";
        list($_, $content) = get($url_page);
        $link_list = get_answer_link_list($content);
        save_answer($base_url, $link_list);
    }
}

function save_answer($base_url, $answer_link_list) {
    foreach ($answer_link_list as $url) {
        $url = $base_url.$url;
        list($_, $content) = get($url);
        list($question, $content) = parse_answer($content);
        $content = '<link rel="stylesheet" href="http://static.zhihu.com/static/ver/f004e446ca569e4897e59cf26da3e2dc.z.css" type="text/css" media="screen,print" />'.$content;
        file_put_contents("$question.html", $content);
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
        throw new Exception("num match fail", 1);
    }
    return (int) max($matches[1]);
}

function get($url, $opts = null) {
    $filename = '/tmp/'.str_replace('/', '-', $url);
    if (file_exists($filename)) {
        return array(0, file_get_contents($filename));
    }

    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $content = curl_exec($ch);
    if ($errno = curl_errno($ch)) {
        return array($errno, curl_error($ch));
    }
    file_put_contents($filename, $content);
    return array(0, $content);
}

