import json
import csv
from typing import Literal
from services.student_service import get_student
from services.grade_service import calc_gpa, get_student_scores, get_rank
from utils import score_to_grade_cn, score_to_grade_letter


ReportFormat = Literal["txt", "csv", "json"]
Lang = Literal["cn", "en"]


def generate_report(
    student_id: int,
    output_path: str,
    fmt: ReportFormat = "txt",
    lang: Lang = "cn",
    show_gpa: bool = True,
    show_rank: bool = False,
    include_comments: bool = True,
) -> bool:
    student = get_student(student_id)
    if student is None:
        print(f"找不到学生 ID={student_id}")
        return False

    scores = get_student_scores(student_id)

    if fmt == "txt":
        return _write_txt(student, scores, output_path, lang, show_gpa, show_rank, include_comments)
    elif fmt == "csv":
        return _write_csv(scores, output_path, lang)
    elif fmt == "json":
        return _write_json(student, scores, output_path, show_gpa)
    return False


def _write_txt(student, scores, path, lang, show_gpa, show_rank, include_comments) -> bool:
    if lang == "cn":
        lines = [
            "学生报告",
            "========",
            f"姓名: {student['name']}",
            f"年龄: {student['age']}",
            f"班级: {student['class']}",
        ]
        if show_gpa:
            lines.append(f"GPA: {calc_gpa(student['id']):.2f}")
        lines.append("\n成绩列表:")
        for sc in scores:
            entry = f"  {sc['course_name']}: {sc['score']} ({score_to_grade_cn(sc['score'])})"
            if include_comments and sc.get("comment"):
                entry += f" [{sc['comment']}]"
            lines.append(entry)
    else:
        lines = [
            "Student Report",
            "==============",
            f"Name: {student['name']}",
            f"Age: {student['age']}",
            f"Class: {student['class']}",
        ]
        if show_gpa:
            lines.append(f"GPA: {calc_gpa(student['id']):.2f}")
        lines.append("\nScores:")
        for sc in scores:
            entry = f"  {sc['course_name']}: {sc['score']} ({score_to_grade_letter(sc['score'])})"
            if include_comments and sc.get("comment"):
                entry += f" [{sc['comment']}]"
            lines.append(entry)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return True


def _write_csv(scores, path, lang) -> bool:
    headers_cn = ["课程", "分数", "考试类型", "日期"]
    headers_en = ["Course", "Score", "Exam Type", "Date"]
    headers = headers_cn if lang == "cn" else headers_en

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for sc in scores:
            writer.writerow([sc["course_name"], sc["score"], sc["exam_type"], sc["date"]])
    return True


def _write_json(student, scores, path, show_gpa) -> bool:
    data = {
        "name": student["name"],
        "age": student["age"],
        "scores": [
            {"course": sc["course_name"], "score": sc["score"],
             "type": sc["exam_type"], "date": sc["date"]}
            for sc in scores
        ],
    }
    if show_gpa:
        data["gpa"] = calc_gpa(student["id"])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True
