<?php

function www_zhihu_com($answer_url) {
    global $root;
        
    // todo support article

    // check url
    if (!preg_match('/\d+$/', $answer_url, $m)) {
        echo "not good url\n";
        exit(1);
    }

    // fetch url
    $html = file_get_contents($answer_url);

    // trans css
    $html = preg_replace_callback('/([^"]+\.css)"/', '_fetch_res', $html);

    // make image visible
    $html = preg_replace_callback('/<img src="([^"]+)" ([^>]+) data-actualsrc="([^"]+)">/', '_zhihu_image_replace', $html);

    // icon of avatar
    $html = preg_replace_callback('/<img ([^>]+) src="([^"]+)"/', '_image_local', $html);

    // todo: video (iframe)
    $html = preg_replace_callback('#<a class="video-box" href="([^"]+)"(.+?</a>)#', '_zhihu_video_replace', $html);

    // trim script or it will cause repeat load problem
    $html = preg_replace('#<script src="https://static.zhihu.com/heifetz/[\-\w\.]+\.js"( async="")?></script>#', '', $html);

    // save
    $id = $m[0];
    $file = "$root/$id.html";
    file_put_contents($file, $html);

    return "$id.html";
}

function _zhihu_image_replace($m) {
    $url = $m[3];
    $new_url = _save_res($url);
    return "<img src=\"$new_url\" $m[2] data-actualsrc=\"$m[3]\">";
}
function _zhihu_video_replace($m) {
    $url = $m[1];
    return '<div class="RichText-video" data-za-detail-view-path-module="VideoItem" data-za-extra-module="{&quot;card&quot;:{&quot;content&quot;:{&quot;type&quot;:&quot;Video&quot;,&quot;sub_type&quot;:&quot;SelfHosted&quot;,&quot;video_id&quot;:&quot;978111777595170816&quot;,&quot;is_playable&quot;:true}}}"><div class="VideoCard VideoCard--interactive"><div class="VideoCard-layout"><div class="VideoCard-video"><div class="VideoCard-video-content"><div class="VideoCard-player"><iframe frameborder="0" allowfullscreen="" src="'.$url.'"></iframe></div></div></div></div><div class="VideoCard-mask"></div></div></div>';
}
