<?php

spl_autoload_register(function ($class_name) {
    $f = dirname(__DIR__).'/'.str_replace('\\', '/', $class_name).'.php';
    if (is_file($f)) {
        require $f;
    }
});
