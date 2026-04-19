<?php

defined('MOODLE_INTERNAL') || die();

$functions = [
    'local_codingengine_upsert_grade' => [
        'classname' => 'local_codingengine\\external\\upsert_grade',
        'methodname' => 'execute',
        'classpath' => '',
        'description' => 'Upsert learner grade and AI feedback from coding engine.',
        'type' => 'write',
        'ajax' => false,
        'capabilities' => 'moodle/grade:edit',
    ],
];

$services = [
    'Coding Engine Service' => [
        'functions' => ['local_codingengine_upsert_grade'],
        'restrictedusers' => 0,
        'enabled' => 1,
        'shortname' => 'codingengine_service',
    ],
];
