"""受入計画とケース別の観察記録を照合する。"""

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


PATHS = {"normal", "failure", "recovery"}
PRIORITIES = {"required", "advisory"}
METHODS = {"automated", "manual"}


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise ValueError(f"JSON キーが重複しています ({key!r})")
        obj[key] = value
    return obj


def reject_constant(token):
    raise ValueError(f"JSON の数値は有限である必要があります ({token})")


def load_object(path):
    try:
        contents = path.read_text(encoding="utf-8-sig")
        value = json.loads(
            contents,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
            parse_float=Decimal,
        )
    except (OSError, ValueError, InvalidOperation, RecursionError) as exc:
        raise ValueError(f"{path.name} を読み込めません ({exc})") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.name} のルートはオブジェクトで指定してください")
    return value


def required_text(record, key, label):
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}.{key} は空でない文字列で指定してください")
    return value


def validate_choice(record, key, choices, label):
    if required_text(record, key, label) not in choices:
        allowed = ", ".join(sorted(choices))
        raise ValueError(f"{label}.{key} に指定できる値は {allowed} です")


def records(document, key):
    values = document.get(key)
    if not isinstance(values, list):
        raise ValueError(f"{key} は配列で指定してください")
    for index, value in enumerate(values):
        label = f"{key}[{index}]"
        if not isinstance(value, dict):
            raise ValueError(f"{label} はオブジェクトで指定してください")
        yield label, value


def validate_checks(record, key, label, *, allow_empty):
    checks = record.get(key)
    if not isinstance(checks, dict) or (not allow_empty and not checks):
        raise ValueError(f"{label}.{key} に確認項目のオブジェクトを指定してください")
    for check_id, value in checks.items():
        if not check_id.strip():
            raise ValueError(f"{label}.{key} に空の確認項目 ID があります")
        if value is None or isinstance(value, (str, int, bool)):
            continue
        if isinstance(value, Decimal) and value.is_finite():
            continue
        raise ValueError(f"{label}.{key}[{check_id!r}] は有限の JSON スカラーで指定してください")


def index_cases(plan):
    cases = {}
    for label, case in records(plan, "cases"):
        case_id = required_text(case, "id", label)
        if case_id in cases:
            raise ValueError(f"ケース ID が重複しています ({case_id!r})")
        required_text(case, "requirement_id", label)
        validate_choice(case, "path", PATHS, label)
        validate_choice(case, "priority", PRIORITIES, label)
        validate_choice(case, "method", METHODS, label)
        validate_checks(case, "expected", label, allow_empty=False)
        cases[case_id] = case
    return cases


def index_observations(log, cases):
    observations = {}
    for label, observer_record in records(log, "observations"):
        case_id = required_text(observer_record, "case_id", label)
        if case_id not in cases:
            raise ValueError(f"計画にないケース ID です ({case_id!r})")
        if case_id in observations:
            raise ValueError(f"ケースの観察記録が重複しています ({case_id!r})")
        validate_choice(observer_record, "method", METHODS, label)
        if "evidence" in observer_record and not isinstance(observer_record["evidence"], str):
            raise ValueError(f"{label}.evidence は文字列で指定してください")
        validate_checks(observer_record, "actual", label, allow_empty=True)
        extra = sorted(observer_record["actual"].keys() - cases[case_id]["expected"].keys())
        if extra:
            raise ValueError(f"{label}.actual に計画外の確認項目があります ({extra!r})")
        observations[case_id] = observer_record
    return observations


def evaluate_case(case, observation):
    expected = case["expected"]
    actual = observation["actual"] if observation is not None else {}
    missing = sorted(expected.keys() - actual.keys())
    mismatched = sorted(
        key
        for key in expected.keys() & actual.keys()
        if type(actual[key]) is not type(expected[key]) or actual[key] != expected[key]
    )

    if observation is None:
        status = "not_run"
    elif observation["method"] != case["method"] or not observation.get("evidence", "").strip():
        status = "insufficient_evidence"
    elif mismatched:
        status = "fail"
    elif missing:
        status = "insufficient_evidence"
    else:
        status = "pass"

    summary = {key: case[key] for key in ("id", "requirement_id", "path", "priority", "method")}
    return {**summary, "status": status, "missing": missing, "mismatched": mismatched}


def evaluate(plan, log):
    task_id = required_text(plan, "task_id", "計画")
    if task_id != required_text(log, "task_id", "観察記録"):
        raise ValueError("計画と観察記録の task_id が一致しません")
    build = required_text(log, "build", "観察記録")
    cases = index_cases(plan)
    observations = index_observations(log, cases)
    results = [evaluate_case(case, observations.get(case_id)) for case_id, case in cases.items()]

    required = [case for case in results if case["priority"] == "required"]
    if any(case["status"] == "fail" for case in required):
        decision = "no_go"
    elif {case["path"] for case in required} != PATHS or any(
        case["status"] != "pass" for case in required
    ):
        decision = "pending"
    else:
        decision = "go"

    observed_paths = {case["path"] for case in results if case["status"] in {"pass", "fail"}}
    normal_passed = any(case["path"] == "normal" and case["status"] == "pass" for case in results)
    if observed_paths == PATHS:
        coverage = "all_paths_observed"
    elif observed_paths == {"normal"} and normal_passed:
        coverage = "normal_only"
    else:
        coverage = "partial"

    return {
        "task_id": task_id,
        "build": build,
        "decision": decision,
        "coverage": coverage,
        "cases": results,
    }


def main():
    parser = argparse.ArgumentParser(description="受入計画と観察記録を照合します。")
    parser.add_argument("plan", metavar="PLAN.json", type=Path)
    parser.add_argument("observations", metavar="OBSERVATIONS.json", type=Path)
    args = parser.parse_args()
    try:
        report = evaluate(load_object(args.plan), load_object(args.observations))
    except ValueError as exc:
        print(f"入力エラー: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["decision"] == "go" else 1


if __name__ == "__main__":
    sys.exit(main())
