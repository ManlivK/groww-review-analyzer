from __future__ import annotations

import csv
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent / "Groww-Review-Pulse"
_VALIDATION_DIR = _PROJECT_DIR / "outputs"
_PROCESSED_DIR = _PROJECT_DIR / "data" / "processed"
_BUILD_GUIDE_PATH = _VALIDATION_DIR / "build_guide_csv_validation.md"
_QUALITY_REPORT_PATH = _VALIDATION_DIR / "data_quality_report.md"
_FULL_ANALYSIS_CSV = _PROCESSED_DIR / "reviews_for_analysis.csv"
_BALANCED_ANALYSIS_CSV = _PROCESSED_DIR / "reviews_balanced_for_analysis.csv"
_CONTENT_COLUMN = "content"
_DATE_COLUMN = "at"
_WEEK_COLUMN = "week_start"
_MIN_REVIEW_WORDS = 2
_ROLLING_WEEKS = 12
_CURRENT_SCOPE = "current"
_HISTORICAL_SCOPE = "historical"


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8")


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))
    except UnicodeDecodeError:
        with path.open("r", encoding="cp1252", newline="") as handle:
            return list(csv.DictReader(handle))


def _word_count(content: Any) -> int:
    return len(str(content or "").strip().split())


def _parse_datetime(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S", "%d/%m/%Y %H:%M"):
            try:
                parsed = datetime.strptime(text, fmt)
                break
            except ValueError:
                continue
        else:
            return None
    return parsed.replace(tzinfo=None)


def _record(
    area: str,
    result: str,
    check: str,
    detail: str,
    source: str,
    scope: str,
) -> dict[str, str]:
    return {
        "area": area,
        "result": result,
        "check": check,
        "detail": detail,
        "source": source,
        "scope": scope,
    }


def _short_review_record(path: Path, label: str) -> dict[str, str]:
    rows = _read_csv_rows(path)
    if not rows:
        return _record(
            "Data",
            "Not available",
            f"{label} short-review validation",
            f"{path.name} is missing or empty.",
            path.name,
            _CURRENT_SCOPE,
        )
    if _CONTENT_COLUMN not in rows[0]:
        return _record(
            "Data",
            "Fail",
            f"{label} short-review validation",
            f"Required '{_CONTENT_COLUMN}' column is missing from {path.name}.",
            path.name,
            _CURRENT_SCOPE,
        )
    short_count = sum(
        _word_count(row.get(_CONTENT_COLUMN)) < _MIN_REVIEW_WORDS for row in rows
    )
    result = "Pass" if short_count == 0 else "Fail"
    return _record(
        "Data",
        result,
        f"{label} short-review validation",
        f"{label}: {len(rows):,} rows; {short_count} reviews with fewer than {_MIN_REVIEW_WORDS} words.",
        path.name,
        _CURRENT_SCOPE,
    )


def _rolling_coverage_record(path: Path) -> dict[str, str]:
    rows = _read_csv_rows(path)
    if not rows:
        return _record(
            "Data",
            "Not available",
            "Current dataset rolling date coverage",
            f"{path.name} is missing or empty.",
            path.name,
            _CURRENT_SCOPE,
        )
    if _DATE_COLUMN not in rows[0] or _WEEK_COLUMN not in rows[0]:
        return _record(
            "Data",
            "Fail",
            "Current dataset rolling date coverage",
            f"Required '{_DATE_COLUMN}' or '{_WEEK_COLUMN}' column is missing from {path.name}.",
            path.name,
            _CURRENT_SCOPE,
        )
    dated = []
    for row in rows:
        at = _parse_datetime(row.get(_DATE_COLUMN))
        week = _parse_datetime(row.get(_WEEK_COLUMN))
        if at is not None and week is not None:
            dated.append((at, week.date()))
    if not dated:
        return _record(
            "Data",
            "Not available",
            "Current dataset rolling date coverage",
            f"No parseable dates found in {path.name}.",
            path.name,
            _CURRENT_SCOPE,
        )
    first_at = min(at for at, _ in dated)
    last_at = max(at for at, _ in dated)
    weeks = sorted({week for _, week in dated})
    span = last_at - first_at
    within_range = span <= timedelta(weeks=_ROLLING_WEEKS)
    first_partial = first_at.date() > weeks[0]
    last_partial = last_at.date() < weeks[-1] + timedelta(days=6)
    monday_buckets = all(week.weekday() == 0 for week in weeks)
    bucket_count = len(weeks)
    boundary_excuse = bucket_count == _ROLLING_WEEKS + 1 and first_partial and last_partial
    allowed = within_range and monday_buckets and (bucket_count <= _ROLLING_WEEKS or boundary_excuse)
    result = "Pass" if allowed else "Fail"
    detail = (
        f"Review dates {first_at:%d %b %Y}–{last_at:%d %b %Y} ({span.total_seconds() / 86400:.1f} days); "
        f"{bucket_count} Monday-based calendar buckets"
    )
    if bucket_count > _ROLLING_WEEKS:
        detail += " with partial first and last weeks" if first_partial and last_partial else " with unexpected boundaries"
    detail += (
        f"; within the configured {_ROLLING_WEEKS}-week rolling range."
        if within_range
        else f"; outside the configured {_ROLLING_WEEKS}-week rolling range."
    )
    if not monday_buckets:
        detail += " One or more week_start values are not Mondays."
    return _record(
        "Data",
        result,
        "Current dataset rolling date coverage",
        detail,
        path.name,
        _CURRENT_SCOPE,
    )


def _clean_inline(text: str) -> str:
    cleaned = text.strip().replace("**", "").replace("`", "")
    return re.sub(r"\s+", " ", cleaned).strip()


def _normalise_result(text: str) -> str:
    value = _clean_inline(text).upper()
    if "FAIL" in value:
        return "Fail"
    if "WARN" in value:
        return "Warning"
    if "PASS" in value:
        return "Pass"
    return "Not available"


def _mentions_ai(text: str) -> bool:
    return bool(re.search(r"\bAI\b", text, flags=re.IGNORECASE))


def _number(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    match = re.search(r"-?\d[\d,]*", str(value))
    if not match:
        return None
    return int(match.group(0).replace(",", ""))


def _table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(cell) <= {"-", ":"} for cell in cells)


def _parse_build_guide(path: Path) -> list[dict[str, str]]:
    text = _read_text(path)
    if not text or "## PASS / FAIL summary" not in text:
        return []
    section = text.split("## PASS / FAIL summary", 1)[1].split("\n## ", 1)[0]
    records: list[dict[str, str]] = []
    for line in section.splitlines():
        cells = _table_cells(line)
        if len(cells) < 4 or _is_separator(cells) or cells[0].lower() == "#":
            continue
        check = _clean_inline(cells[1])
        detail = _clean_inline(cells[3])
        if _mentions_ai(f"{check} {detail}"):
            continue
        records.append(
            {
                "area": "Data",
                "result": _normalise_result(cells[2]),
                "check": check,
                "detail": detail,
                "source": path.name,
            }
        )
    return records


def _parse_quality_report(path: Path) -> list[dict[str, str]]:
    text = _read_text(path)
    if not text:
        return []
    records: list[dict[str, str]] = []
    current_heading = ""
    pii_counts: list[tuple[str, str, str]] = []
    result_pattern = re.compile(
        r"^(.*?)\bResult:\s*\*\*(PASS|FAIL|WARN[A-Z]*)\*\*\s*[—–-]?\s*(.*)$",
        flags=re.IGNORECASE,
    )
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            current_heading = _clean_inline(stripped[3:])
            continue
        match = result_pattern.match(stripped)
        if match:
            prefix = _clean_inline(match.group(1))
            check = prefix or current_heading or "Validation check"
            detail = _clean_inline(match.group(3))
            if _mentions_ai(f"{check} {detail}"):
                continue
            records.append(
                {
                    "area": "Data",
                    "result": _normalise_result(match.group(2)),
                    "check": check,
                    "detail": detail,
                    "source": path.name,
                }
            )
            continue
        if current_heading.lower() == "pii redaction":
            cells = _table_cells(stripped)
            if len(cells) >= 3 and not _is_separator(cells) and cells[0].lower() != "pii type":
                pii_counts.append((_clean_inline(cells[0]), cells[1], cells[2]))
    if pii_counts:
        detail = "; ".join(
            f"{label}: {_clean_inline(full)} full / {_clean_inline(balanced)} balanced"
            for label, full, balanced in pii_counts
            if not _mentions_ai(label)
        )
        if detail:
            records.append(
                {
                    "area": "Security",
                    "result": "Pass" if all(_number(v) is not None for _, f, b in pii_counts for v in (f, b)) else "Not available",
                    "check": "PII redaction patterns applied",
                    "detail": detail,
                    "source": path.name,
                }
            )
    return records


def _analysed_review_total(data: dict[str, Any]) -> int | None:
    for row in _get(data, "overview", "kpis", default=[]):
        label = str(row.get("label", "")).lower()
        if "review" in label and "analys" in label:
            return _number(row.get("value"))
    return None


def _get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return default
        value = value.get(key)
    return default if value is None else value


def _theme_record(data: dict[str, Any]) -> dict[str, str]:
    analysed = _analysed_review_total(data)
    themes = data.get("themes", []) or []
    counts = [_number(row.get("count")) for row in themes if isinstance(row, dict)]
    valid_counts = [count for count in counts if count is not None]
    total = sum(valid_counts)
    if analysed is None or len(valid_counts) != len(themes):
        result = "Not available"
        detail = "Theme counts or analysed review total are not available in report.json."
    else:
        result = "Pass" if total == analysed else "Fail"
        detail = f"Theme counts total {total:,}; analysed reviews total {analysed:,}."
    return {
        "area": "Themes",
        "result": result,
        "check": "Theme counts reconcile to analysed reviews",
        "detail": detail,
        "source": "report.json",
    }


def _contains_quote_data(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            label = str(key).lower()
            if "quote" in label or label in {"review_text", "verbatim", "content"}:
                return True
            if _contains_quote_data(child):
                return True
    elif isinstance(value, list):
        return any(_contains_quote_data(child) for child in value)
    return False


def _quote_record(data: dict[str, Any]) -> dict[str, str]:
    has_quote_data = _contains_quote_data(data)
    return {
        "area": "Quotes",
        "result": "Pass" if has_quote_data else "Warning",
        "check": "Verbatim quote availability",
        "detail": (
            "Verbatim quote data is present in report.json."
            if has_quote_data
            else "Verbatim review text is not present in report.json; only aggregated excerpts are available."
        ),
        "source": "report.json",
    }


def _week_values(rows: Any) -> set[str]:
    if not isinstance(rows, list):
        return set()
    return {str(row.get("week")) for row in rows if isinstance(row, dict) and row.get("week")}


def _weekly_record(data: dict[str, Any]) -> dict[str, str]:
    series = {
        "weekly volume": _get(data, "trends", "weekly_volume", default=[]),
        "rating trend": _get(data, "trends", "rating_trend", default=[]),
        "rating split": _get(data, "trends", "rating_split", default=[]),
        "overview rating trend": _get(data, "overview", "weekly_rating_trend", default=[]),
    }
    week_sets = [_week_values(rows) for rows in series.values()]
    week_sets = [week_set for week_set in week_sets if week_set]
    if not week_sets:
        result = "Not available"
        detail = "Weekly series are not available in report.json."
    elif len({frozenset(week_set) for week_set in week_sets}) == 1:
        result = "Pass"
        detail = f"Weekly volume, rating and split series cover the same {len(week_sets[0])} weeks."
    else:
        result = "Fail"
        detail = "Weekly series cover different week sets in report.json."
    return {
        "area": "Weekly Pulse",
        "result": result,
        "check": "Weekly series alignment",
        "detail": detail,
        "source": "report.json",
    }


def _fee_record(data: dict[str, Any]) -> dict[str, str]:
    fees = data.get("fee_analysis", {}) or {}
    fact_check = fees.get("fact_check", []) or []
    sources = fees.get("sources", []) or []
    approved = any(
        "approved" in str(row.get("status", "")).lower()
        for row in fact_check
        if isinstance(row, dict)
    )
    pilot = _number(fees.get("pilot_sample_size"))
    related = _number(fees.get("fee_related_review_count"))
    if not fact_check:
        result = "Not available"
        detail = "Fee fact-check results are not available in report.json."
    elif not sources:
        result = "Fail"
        detail = "No official sources are recorded for the fee explainer."
    elif not approved:
        result = "Fail"
        detail = "Fee fact-check results do not record an approved status."
    elif pilot is not None and related is not None and pilot < related:
        result = "Warning"
        detail = (
            f"Fact-check approved with {len(sources)} official sources; "
            f"pilot classified {pilot} of {related} fee-related reviews."
        )
    else:
        result = "Pass"
        detail = f"Fact-check approved with {len(sources)} official sources."
    return {
        "area": "Fee Explainer",
        "result": result,
        "check": "Fee explainer fact-check",
        "detail": detail,
        "source": "report.json",
    }


_SOURCE_PRIORITY = {
    _QUALITY_REPORT_PATH.name: 0,
    _FULL_ANALYSIS_CSV.name: 1,
    _BALANCED_ANALYSIS_CSV.name: 1,
    "report.json": 2,
}


def _scoped(records: list[dict[str, str]], scope: str) -> list[dict[str, str]]:
    return [dict(record, scope=scope) for record in records]


def _dedupe(records: list[dict[str, str]]) -> list[dict[str, str]]:
    best: dict[str, tuple[int, dict[str, str]]] = {}
    for record in records:
        key = re.sub(r"\W+", " ", record["check"]).strip().lower()
        priority = _SOURCE_PRIORITY.get(record["source"], 99)
        if key not in best or priority < best[key][0]:
            best[key] = (priority, record)
    return [item[1] for item in best.values()]


def current_validation_sources() -> list[tuple[str, Path]]:
    return [
        ("Authoritative quality report", _QUALITY_REPORT_PATH),
        ("Full analysis CSV", _FULL_ANALYSIS_CSV),
        ("Balanced analysis CSV", _BALANCED_ANALYSIS_CSV),
        ("Dashboard payload", Path(__file__).with_name("report.json")),
    ]


def load_current_validation_records(data: dict[str, Any]) -> list[dict[str, str]]:
    records = _parse_quality_report(_QUALITY_REPORT_PATH)
    records.append(_short_review_record(_FULL_ANALYSIS_CSV, "Full analysis dataset"))
    records.append(_short_review_record(_BALANCED_ANALYSIS_CSV, "Balanced analysis dataset"))
    records.append(_rolling_coverage_record(_FULL_ANALYSIS_CSV))
    records.append(_theme_record(data))
    records.append(_quote_record(data))
    records.append(_weekly_record(data))
    records.append(_fee_record(data))
    records = _scoped(records, _CURRENT_SCOPE)
    return [record for record in _dedupe(records) if not _mentions_ai(" ".join(record.values()))]


def load_reference_records() -> list[dict[str, str]]:
    records = _scoped(_parse_build_guide(_BUILD_GUIDE_PATH), _HISTORICAL_SCOPE)
    return [record for record in records if not _mentions_ai(" ".join(record.values()))]


def load_validation_records(data: dict[str, Any]) -> list[dict[str, str]]:
    return load_current_validation_records(data)


def summarise_counts(records: list[dict[str, str]]) -> dict[str, int]:
    return {
        "total": len(records),
        "passed": sum(record["result"] == "Pass" for record in records),
        "failed": sum(record["result"] == "Fail" for record in records),
        "warnings": sum(record["result"] == "Warning" for record in records),
    }


def summarise_areas(records: list[dict[str, str]]) -> list[dict[str, str]]:
    areas = ["Data", "Themes", "Quotes", "Weekly Pulse", "Fee Explainer", "Security"]
    rows: list[dict[str, str]] = []
    for area in areas:
        area_records = [record for record in records if record["area"] == area]
        if not area_records:
            rows.append(
                {
                    "area": area,
                    "result": "Not available",
                    "check": "Validation results are not available for this area.",
                }
            )
            continue
        failed = [record for record in area_records if record["result"] == "Fail"]
        warnings = [record for record in area_records if record["result"] == "Warning"]
        passed = [record for record in area_records if record["result"] == "Pass"]
        if failed:
            result = "Fail"
            names = [record["check"] for record in failed]
            check = f"{len(failed)} failed checks: " + "; ".join(names[:2])
            if len(names) > 2:
                check += f"; +{len(names) - 2} more"
        elif warnings:
            result = "Warning"
            check = "; ".join(f"{record['check']}: {record['detail']}" for record in warnings[:1])
        elif passed:
            result = "Pass"
            check = "; ".join(f"{record['check']}: {record['detail']}" for record in passed[:1])
            if len(area_records) > 1:
                check = f"{len(passed)} checks passed; {check}"
        else:
            result = "Not available"
            check = "Validation results are not available for this area."
        rows.append({"area": area, "result": result, "check": check})
    return rows
