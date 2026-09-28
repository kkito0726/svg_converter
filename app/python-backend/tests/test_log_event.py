import json

from log_event import LogEvent


def test_events_match_design_doc():
    # docs/logging-design.md 3.2 の一覧と揃える。変更するときは設計書も更新すること
    assert {event.value for event in LogEvent} == {
        "request.completed",
        "request.log_failed",
        "convert.completed",
        "convert.failed",
    }


def test_event_is_serialized_as_plain_string():
    assert json.dumps({"event": LogEvent.CONVERT_COMPLETED}) == '{"event": "convert.completed"}'
