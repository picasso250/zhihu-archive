<?php

function www_zhihu_com($answer_url) {
        
    // todo support article
    // todo support people's answer and fav list

    if (preg_match('#/people/(.+)/answers#', $answer_url, $m)) {
        // people's answer
        echo "fetch $m[1]\n";
        return _zhihu_people_answer_list($answer_url, $m[1]);
    }

    // check url
    if (!preg_match('/\d+$/', $answer_url, $m)) {
        echo "not good url\n";
        exit(1);
    }

    return _zhihu_one_answer($answer_url);
}

function _zhihu_one_answer($answer_url) {
    global $root;

    // fetch url
    $html = file_get_contents($answer_url);

    // trans css
    $html = preg_replace_callback('/"([^"]+\.css)"/', '_fetch_res', $html);

    // make image visible
    $html = preg_replace_callback('/<img src="([^"]+)" ([^>]+) data-actualsrc="([^"]+)">/', '_zhihu_image_replace', $html);

    // icon of avatar
    $html = preg_replace_callback('/<img ([^>]+) src="([^"]+)"/', '_zhihu_image_local', $html);

    // video (iframe)
    $html = preg_replace_callback('#<a class="video-box" href="([^"]+)"(.+?</a>)#', '_zhihu_video_replace', $html);

    // trim script or it will cause repeat load problem
    $html = preg_replace('#<script src="https://static.zhihu.com/heifetz/[\-\w\.]+\.js"( async="")?></script>#', '', $html);

    // save
    $id = $m[0];
    $file = "$root/$id.html";
    file_put_contents($file, $html);

    return "$id.html";
}

function _zhihu_people_answer_list($url, $username) {
    global $root;

    // get html template
    $raw_html = http_get($url);

    // total pages
    $total = 1;
    if (preg_match_all('/class="Button PaginationButton Button--plain">(\d+)/', $raw_html, $m)) {
        $m1 = $m[1];
        $total = intval($m1[count($m1)-1]);
    }

    foreach (range(1,$total) as $_ => $index) {
        echo $url."\tpage=$index\n";
        $html = _zhihu_people_answer_one_page($raw_html, $index, $total, $username);
        $file = "$root/${username}_$index.html";
        file_put_contents($file, $html);
    }

    return "${username}_1.html";
}

function _zhihu_people_answer_one_page($html, $page, $total, $username) {
    global $root;

    // load answers
    $per_page = 20;
    $offset = ($page-1)*$per_page;
    $json_root = "$root/json";
    if (!is_dir($json_root)) mkdir($json_root);
    $json_file = "$json_root/$username.$offset.$per_page.json";
    if (is_file($json_file)) {
        echo "get $json_file from cache\n";
        $jc = file_get_contents($json_file);
    } else {
        sleep(1);
        echo "get json: $username.$offset.$per_page\n";
        $jc = _zhihu_get_answer_ajax($username, $offset, $per_page);
        file_put_contents($json_file, $jc);
    }
    $j = json_decode($jc, true);

    // render answer
    echo "render answer\n";
    $as=[];
    foreach ($j['data'] as $key => $answer) {
        $question_title = $answer['question']['title'];
        $avatar_img=str_replace('{size}','xs',$answer['author']['avatar_url_template']);
        $uid=$username;
        $name=$answer['author']['name'];
        $content=$answer['content'];
        $date=date('Y-m-d', $answer['created_time']);
        $up_vote=$answer['voteup_count'];
        $comment_num=$answer['comment_count'];
        ob_start();
        include 'item.php';
        $as[] = ob_get_clean();
    }
    $as = implode(',',$as);


    // replace answers
    $html = preg_replace('/<div class="List-item">.+<div class="Pagination"/', $as.'<div class="Pagination"', $html);

    // replace page link
    $html = preg_replace('#<div class="Pagination">(.+?)</div>#', '<div class="Pagination">'._zhihu_page_link_html($username, $page, $total).'</div>', $html);

    echo "trans css\n";
    // trans css
    $html = preg_replace_callback('/"([^"]+\.css)"/', '_fetch_res', $html);
    // $html = preg_replace_callback('/([^"]+\.js)"/', '_fetch_res', $html);

    echo "make image visible\n";
    // make image visible
    $html = preg_replace_callback('/<img src="([^"]+)" ([^>]+) data-actualsrc="([^"]+)">/', '_zhihu_image_replace', $html);

    // icon of avatar
    $html = preg_replace_callback('/<img ([^>]+) src="([^"]+)"/', '_zhihu_image_local', $html);

    // video (iframe)
    $html = preg_replace_callback('#<a class="video-box" href="([^"]+)"(.+?</a>)#', '_zhihu_video_replace', $html);

    // trim script or it will cause repeat load problem
    $html = preg_replace('#<script src="https://static.zhihu.com/heifetz/[\-\w\.]+\.js"( async="")?></script>#', '', $html);

    return $html;
}

function _zhihu_image_replace($m) {
    // skip data:image/svg+xml
    if (strpos($m[1],'data') === 0) return $m[0];

    $url = $m[3];
    $new_url = _save_res($url);
    return "<img src=\"$new_url\" $m[2] data-actualsrc=\"$m[3]\">";
}
function _zhihu_video_replace($m) {
    $url = $m[1];
    return '<div class="RichText-video" data-za-detail-view-path-module="VideoItem" data-za-extra-module="{&quot;card&quot;:{&quot;content&quot;:{&quot;type&quot;:&quot;Video&quot;,&quot;sub_type&quot;:&quot;SelfHosted&quot;,&quot;video_id&quot;:&quot;978111777595170816&quot;,&quot;is_playable&quot;:true}}}"><div class="VideoCard VideoCard--interactive"><div class="VideoCard-layout"><div class="VideoCard-video"><div class="VideoCard-video-content"><div class="VideoCard-player"><iframe frameborder="0" allowfullscreen="" src="'.$url.'"></iframe></div></div></div></div><div class="VideoCard-mask"></div></div></div>';
}
function _zhihu_page_link($uid, $page, $text, $disabled=false) {
    if ($disabled)
        return '<button type="button" class="Button PaginationButton PaginationButton--current Button--plain" disabled="">'.$text.'</button>';
    return "<a href=\"${uid}_$page.html\" type=\"button\" class=\"Button PaginationButton Button--plain\">$text</a>";
}
function _zhihu_page_link_html($uid, $page, $total) {
    $ret=[];
    foreach (range(1,$total) as $p) {
        $ret[] = _zhihu_page_link($uid, $p, $p, $p==$page);
    }
    return implode('',$ret);
}
function _zhihu_image_local($m) {
    $url = $m[2];

    // skip qrcode
    if (strpos($url,'qrcode?')) return $m[0];

    // skip dataimage/svg+xml
    if (strpos($m[1],'data') === 0) return $m[0];

    $new_url = _save_res($url);
    return "<img $m[1] src=\"$new_url\"";
}

function http_get($url) {
    // Generated by curl-to-PHP: http://incarnate.github.io/curl-to-php/
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "GET");

    $headers = array();
    $headers[] = "Authority: www.zhihu.com";
    $headers[] = "Pragma: no-cache";
    $headers[] = "Cache-Control: no-cache";
    $headers[] = "Upgrade-Insecure-Requests: 1";
    $headers[] = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36";
    $headers[] = "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8";
    $headers[] = "Accept-Language: zh-CN,zh;q=0.9";
    $headers[] = "Cookie: tgw_l7_route=27a99ac9a31c20b25b182fd9e44378b8; _xsrf=38a65421-4eda-4b29-9a5c-dfc380d43cbe; d_c0=\"ANDlpzWarQ2PTjQWGNp-_-89RJV13Xi9bmk=|1527768557\"; q_c1=07633d0386904788a6f652cdd504929c|1527768557000|1527768557000; _zap=032ab6cc-e29c-438c-a5d7-5335a562d525; l_n_c=1; l_cap_id=\"NDEyMjk2M2YxNTUxNDI1MWFkYzNhZTBlZDU5MDM2Nzk=|1527768608|4348954f076bd21a3d16175a8ab7377278be04e3\"; r_cap_id=\"ZjA0ODNkY2JmNjc5NGRlODhkYmQ0OGUzMDY0NzZiNmY=|1527768608|1c4327bbed970485731ea340e7007511b4d42fe0\"; cap_id=\"MmUzY2IwMDVkNTA3NGUxZmFiZGNhMGU1NWZjODg1YzU=|1527768608|84e9dc352253a14773347ebd39df74050c0ec36f\"; n_c=1";
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

    $result = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error:' . curl_error($ch);
    }
    curl_close ($ch);

    return $result;
}

function _zhihu_get_answer_ajax($uid, $offset, $limit = 20) {
    // Generated by curl-to-PHP: http://incarnate.github.io/curl-to-php/
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, "https://www.zhihu.com/api/v4/members/$uid/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cvoting%2Cis_author%2Cis_thanked%2Cis_nothelp%3Bdata%5B*%5D.author.badge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=$offset&limit=$limit&sort_by=created");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, "GET");

    $headers = array();
    $headers[] = "Pragma: no-cache";
    $headers[] = "Cookie: _xsrf=66350f1e-c444-460e-8652-0c3253793c98; d_c0=\"APBk21uerQ2PTiyqHw_UUWzffirOYKU8_X8=|1527769645\"; q_c1=018884fb02774057b4583fea95925da9|1527769645000|1527769645000; _zap=4cb36bfd-a274-4432-beea-537f64836522; l_n_c=1; l_cap_id=\"MmEwZDI0ZWMzM2I3NDFjNDk2ZjZjYWI5OTU0ODVkYmQ=|1527770894|3dec8d2442bc17616ffc4d5b078bd2e5cc0c8dd1\"; r_cap_id=\"ZTE4N2IxY2Y0YWMxNGE1NWE0ZjdjMmE5NjdiNWE1YmI=|1527770894|65fd47754205885dad888802ff49044ccae66ce9\"; cap_id=\"M2VjZjI3NjMyNjQ4NGI3MGI3YmIzZThlNzNmMDY3YTM=|1527770894|8e6b50f6af2b7ead961afdcf41f4ccda01ab468c\"; n_c=1; tgw_l7_route=170010e948f1b2a2d4c7f3737c85e98c";
    $headers[] = "Accept-Language: zh-CN,zh;q=0.9";
    $headers[] = "Authorization: oauth c3cef7c66a1843f8b3a9e6a1e3160e20";
    $headers[] = "Accept: application/json, text/plain, */*";
    $headers[] = "Cache-Control: no-cache";
    $headers[] = "Authority: www.zhihu.com";
    $headers[] = "X-Udid: APBk21uerQ2PTiyqHw_UUWzffirOYKU8_X8=";
    $headers[] = "Referer: https://www.zhihu.com/people/wang-xiao-chi/answers";
    $headers[] = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36";
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

    $result = curl_exec($ch);
    if (curl_errno($ch)) {
        echo 'Error:' . curl_error($ch);
    }
    curl_close ($ch);

    return $result;
}