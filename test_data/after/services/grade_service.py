from typing import Optional
from database import get_db
from models import Score, ExamType, ClassStats


def add_score(score: Score) -> int:
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO scores (student_id, course_id, score, exam_type, date, teacher, comment)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (score.student_id, score.course_id, score.score, score.exam_type.value,
             score.date, score.teacher, score.comment),
        )
        return cursor.lastrowid


def get_student_scores(student_id: int, course_id: Optional[int] = None) -> list[dict]:
    params: list = [student_id]
    sql = """SELECT s.score, s.exam_type, s.date, s.comment, c.name as course_name
             FROM scores s JOIN courses c ON s.course_id = c.id
             WHERE s.student_id = ?"""
    if course_id is not None:
        sql += " AND s.course_id = ?"
        params.append(course_id)

    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def calc_gpa(student_id: int) -> float:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT score FROM scores WHERE student_id = ?", (student_id,)
        ).fetchall()

    if not rows:
        return 0.0

    gpa_points = [Score(student_id, 0, r["score"], ExamType.FINAL, "", "").gpa_points
                  for r in rows]
    return sum(gpa_points) / len(gpa_points)


def get_rank(student_id: int, course_id: int) -> int:
    with get_db() as conn:
        my_row = conn.execute(
            "SELECT score FROM scores WHERE student_id = ? AND course_id = ?",
            (student_id, course_id),
        ).fetchone()

        if my_row is None:
            return -1

        higher_count = conn.execute(
            "SELECT COUNT(*) FROM scores WHERE course_id = ? AND score > ?",
            (course_id, my_row["score"]),
        ).fetchone()[0]

    return higher_count + 1


def get_class_stats(class_name: str, course_id: Optional[int] = None,
                    year: Optional[int] = None) -> Optional[ClassStats]:
    with get_db() as conn:
        student_ids = [
            r["id"] for r in conn.execute(
                "SELECT id FROM students WHERE class = ?", (class_name,)
            ).fetchall()
        ]

        if not student_ids:
            return None

        placeholders = ",".join("?" * len(student_ids))
        sql = f"SELECT score FROM scores WHERE student_id IN ({placeholders})"
        params: list = list(student_ids)

        if course_id is not None:
            sql += " AND course_id = ?"
            params.append(course_id)
        if year is not None:
            sql += " AND date LIKE ?"
            params.append(f"{year}%")

        scores = [r["score"] for r in conn.execute(sql, params).fetchall()]

    if not scores:
        return ClassStats(class_name, len(student_ids), 0, 0.0, 0.0, 0.0, 0, 0)

    return ClassStats(
        class_name=class_name,
        student_count=len(student_ids),
        score_count=len(scores),
        average=sum(scores) / len(scores),
        maximum=max(scores),
        minimum=min(scores),
        pass_count=sum(1 for s in scores if s >= 60),
        excellent_count=sum(1 for s in scores if s >= 90),
    )
