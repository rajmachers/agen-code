<?php

namespace local_codingengine\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/externallib.php');

use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class upsert_grade extends external_api {
    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'userid' => new external_value(PARAM_INT, 'User id'),
            'assignmentid' => new external_value(PARAM_TEXT, 'External assignment id'),
            'score' => new external_value(PARAM_FLOAT, 'Score in percentage'),
            'feedback' => new external_value(PARAM_RAW, 'AI formative feedback'),
        ]);
    }

    public static function execute(
        int $userid,
        string $assignmentid,
        float $score,
        string $feedback
    ): array {
        global $DB;

        self::validate_context(\context_system::instance());

        $record = (object) [
            'userid' => $userid,
            'assignmentid' => $assignmentid,
            'score' => $score,
            'feedback' => $feedback,
            'timeupdated' => time(),
        ];

        // In production, map assignmentid to grade item and call grade APIs.
        // Temporary persistence table expected in a later migration.
        if ($DB->get_manager()->table_exists('local_codingengine_grade')) {
            $existing = $DB->get_record('local_codingengine_grade', [
                'userid' => $userid,
                'assignmentid' => $assignmentid,
            ]);
            if ($existing) {
                $record->id = $existing->id;
                $DB->update_record('local_codingengine_grade', $record);
            } else {
                $record->timecreated = time();
                $DB->insert_record('local_codingengine_grade', $record);
            }
        }

        return [
            'status' => 'ok',
            'message' => 'Grade sync accepted.',
        ];
    }

    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'status' => new external_value(PARAM_TEXT, 'Result status'),
            'message' => new external_value(PARAM_TEXT, 'Result message'),
        ]);
    }
}
