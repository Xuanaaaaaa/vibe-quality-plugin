import csv
from typing import Optional
from database import get_db
from models import Student, Gender


def add_student(student: Student) -> int:
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO students (name, age, gender, class, email, phone, address, grade)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (student.name, student.age, student.gender.value, student.class_name,
             student.email, student.phone, student.address, student.grade),
        )
        return cursor.lastrowid


def get_student(student_id: int) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()
    return dict(row) if row else None


def update_student(student_id: int, student: Student) -> bool:
    with get_db() as conn:
        affected = conn.execute(
            """UPDATE students
               SET name=?, age=?, gender=?, class=?, email=?, phone=?, address=?, grade=?
               WHERE id=?""",
            (student.name, student.age, student.gender.value, student.class_name,
             student.email, student.phone, student.address, student.grade, student_id),
        ).rowcount
    return affected > 0


def delete_student(student_id: int) -> bool:
    with get_db() as conn:
        affected = conn.execute(
            "DELETE FROM students WHERE id = ?", (student_id,)
        ).rowcount
    return affected > 0


def search_students(
    keyword: str = "",
    field: str = "name",
    grade: str = "",
    class_name: str = "",
    gender: str = "",
    sort_by: str = "name",
    descending: bool = False,
) -> list[dict]:
    allowed_fields = {"name", "email", "address", "phone"}
    allowed_sort = {"name", "age", "class", "grade"}

    if field not in allowed_fields:
        field = "name"
    if sort_by not in allowed_sort:
        sort_by = "name"

    order = "DESC" if descending else "ASC"
    conditions = []
    params: list = []

    if keyword:
        conditions.append(f"{field} LIKE ?")
        params.append(f"%{keyword}%")
    if grade:
        conditions.append("grade = ?")
        params.append(grade)
    if class_name:
        conditions.append("class = ?")
        params.append(class_name)
    if gender:
        conditions.append("gender = ?")
        params.append(gender)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"SELECT * FROM students {where} ORDER BY {sort_by} {order}"

    with get_db() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]


def bulk_import_csv(filepath: str) -> tuple[int, int]:
    success = 0
    errors = 0
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                student = Student(
                    name=row["name"],
                    age=int(row["age"]),
                    gender=Gender(row["gender"].upper()),
                    class_name=row["class"],
                    email=row["email"],
                    phone=row["phone"],
                    address=row["address"],
                    grade=row["grade"],
                )
                add_student(student)
                success += 1
            except (KeyError, ValueError):
                errors += 1
    return success, errors
