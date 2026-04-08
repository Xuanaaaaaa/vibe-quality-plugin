import datetime
from typing import Any


PASS_THRESHOLD = 60
EXCELLENT_THRESHOLD = 90


def score_to_grade_cn(score: float) -> str:
    thresholds = [
        (EXCELLENT_THRESHOLD, "优秀"),
        (80, "良好"),
        (70, "中等"),
        (PASS_THRESHOLD, "及格"),
    ]
    for threshold, label in thresholds:
        if score >= threshold:
            return label
    return "不及格"


def score_to_grade_letter(score: float) -> str:
    thresholds = [(EXCELLENT_THRESHOLD, "A"), (80, "B"), (70, "C"), (PASS_THRESHOLD, "D")]
    for threshold, letter in thresholds:
        if score >= threshold:
            return letter
    return "F"


def format_name(name: str) -> str:
    return name.strip().title()


def get_current_semester() -> str:
    now = datetime.datetime.now()
    if now.month >= 9 or now.month <= 1:
        return f"{now.year}-{now.year + 1} 上学期"
    return f"{now.year - 1}-{now.year} 下学期"


def print_table(headers: list[str], rows: list[list[Any]]) -> None:
    widths = [
        max(len(str(h)), max((len(str(r[i])) for r in rows if i < len(r)), default=0))
        for i, h in enumerate(headers)
    ]
    header_line = "  ".join(str(h).ljust(w) for h, w in zip(headers, widths))
    print(header_line)
    print("-" * len(header_line))
    for row in rows:
        print("  ".join(str(row[i] if i < len(row) else "").ljust(w)
                         for i, w in enumerate(widths)))
