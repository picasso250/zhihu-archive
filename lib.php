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
