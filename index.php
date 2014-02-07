<?php

error_reporting(E_ALL|E_STRICT);

require __DIR__.'/vendor/autolaod.php';

$klein = new Klein/Klein;

$klein->respond('GET', '/', );
$klein->dispatch();
