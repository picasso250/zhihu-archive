#coding: utf-8

require dirname(dirname(__DIR__))."/vendor/autoload.php";
require dirname(__DIR__)."/odie.php";
require dirname(__DIR__)."/logic.php";
require (__DIR__)."/lib_mongodb.php";
require (__DIR__)."/autoload.php";

use model\User;
use model\Question;
use model\Answer;

$base_url = 'http://www.zhihu.com';

$ids = Question::getIds();
echo "there are ",count($ids)," questions to fetch\n";

foreach ($ids as $qid) {
    $url = "$base_url/question/$qid";
    list($code, $content) = odie_get($url);
    echo "fetch $qid [$code]\n";
    $username_list = get_username_list($content);

    foreach ($username_list as $username => $nickname) {
        echo "\t$username";
        User::saveUser($username, $nickname);
    }
    echo "\n";
    Question::setFetched($qid);
}


#coding: utf-8
