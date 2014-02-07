<?php

return array(
    'routers' => array(
        array('GET', '/', array('index', 'index')),
        array('GET', '/question/[:id]', array('question', 'view')),
        array('GET', '/question/[:id]/answer/[:aid]', array('answer', 'view')),
        array('GET', '/people/[:name]', array('user', 'view')),
        array('POST', '/', array('index', 'index')),
        array('GET', '/', array('index', 'index')),
        array('GET', '/', array('index', 'index')),
        array('GET', '/', array('index', 'index')),
        array('GET', '/', array('index', 'index')),
    ),
);
