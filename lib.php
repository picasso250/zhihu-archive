<?php

function _get($key = null, $default = null)
{
    if ($key === null)
        return $_GET;
    return isset($_GET[$key]) ? ($_GET[$key]) : $default;
}
function _post($key = null, $default = null)
{
    if ($key === null)
        return $_POST;
    return isset($_POST[$key]) ? ($_POST[$key]) : $default;
}
function _req($key = null, $default = null)
{
    if ($key === null)
        return $_REQUEST;
    return isset($_REQUEST[$key]) ? ($_REQUEST[$key]) : $default;
}

function app_log($msg)
{
    // /home/bae/log/app.log
    $dir = __DIR__;
    $file = $dir.'/app.log';
    $msg = call_user_func_array('sprintf', func_get_args());
    $msg = sprintf("[%s] %s\n", date('Y-m-d H:i:s'), $msg);
    return error_log($msg, 3, $file);
}
