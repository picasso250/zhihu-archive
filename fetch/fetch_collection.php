<?php

require dirname(__DIR__)."/vendor/autoload.php";
require (__DIR__)."/odie.php";

$coid = '20430715';
if (isset($argv[1])) {
    $coid = $argv[1];
}
$base_url = 'https://www.zhihu.com';
$url = "$base_url/collection/$coid";
echo "fetch $url\n";
// list($code, $content) = odie_get($url);
$code = 200;
$content = file_get_contents(__DIR__.'/cache/'.urlencode($url));
// echo "$code\t$content\n";
if ($code == 404) {
    echo "没有这个收藏 $coid\n";
    exit(1);
}

phpQuery::newDocumentHtml($content);
// echo count(pq('textarea.content')),PHP_EOL;
$n = get_page_num();
echo "$n pages\n";
if ($n == 0) {
  echo "no page\n";
  exit(1);
}
for ($i=1; $i <= $n; $i++) {
  $purl = "$url?page=$i";
  echo "$purl\n";
  // list($code, $content) = odie_get($purl);
  phpQuery::newDocumentHtml($content);
  echo count(pq('textarea.content')),PHP_EOL;
  pq('post-content')->each(function($e) {
    $
    echo html_entity_decode(pq($e)->html());
  })
  pq('textarea.content')->each(function($e) {
    echo html_entity_decode(pq($e)->html());
  });
exit;
}

function get_page_num() {
  $arr = pq('.border-pager a')->map(function ($e) {
    $href = pq($e)->attr('href');
    $a = explode('=', $href);
    if (count($a) == 2) {
      return intval($a[1]);
    }
    return 0;
  })->get();
  rsort($arr);
  return count($arr) > 0 ? $arr[0] : 0;
}
