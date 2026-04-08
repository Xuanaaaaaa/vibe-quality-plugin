import sys
from database import create_tables, authenticate_user
from services.student_service import add_student, search_students, bulk_import_csv
from services.grade_service import add_score, calc_gpa, get_class_stats
from report_generator import generate_report
from models import Student, Score, Gender, ExamType


def main():
    create_tables()

    user = authenticate_user("admin", "changeme")
    if not user:
        print("登录失败")
        sys.exit(1)

    print(f"已登录: {user['username']} ({user['role']})")

    student = Student(
        name="张三",
        age=18,
        gender=Gender.MALE,
        class_name="高三1班",
        email="zhangsan@example.com",
        phone="13800138001",
        address="北京市海淀区",
        grade="高三",
    )
    student_id = add_student(student)
    print(f"添加学生成功，ID={student_id}")

    score = Score(
        student_id=student_id,
        course_id=1,
        score=88.5,
        exam_type=ExamType.FINAL,
        date="2026-01-15",
        teacher="李老师",
        comment="表现良好",
    )
    add_score(score)

    gpa = calc_gpa(student_id)
    print(f"GPA: {gpa:.2f}")

    stats = get_class_stats("高三1班")
    if stats:
        print(f"班级平均分: {stats.average:.1f}，及格率: {stats.pass_rate:.1f}%")

    generate_report(student_id, "report.txt", fmt="txt", lang="cn")
    print("报告已生成: report.txt")


if __name__ == "__main__":
    main()
