import json

from error_reason import ErrorReason


def test_reason_codes_match_design_doc():
    # docs/logging-design.md 3.3 の一覧と揃える。変更するときは設計書も更新すること
    assert {reason.value for reason in ErrorReason} == {
        "missing_params",
        "invalid_params",
        "out_of_range",
        "no_file",
        "invalid_extension",
        "invalid_svg",
        "too_large",
        "internal_error",
    }


def test_reason_is_serialized_as_plain_string():
    assert json.dumps({"reason": ErrorReason.OUT_OF_RANGE}) == '{"reason": "out_of_range"}'
    assert ErrorReason.OUT_OF_RANGE == "out_of_range"
