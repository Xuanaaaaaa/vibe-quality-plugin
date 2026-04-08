from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Gender(str, Enum):
    MALE = "M"
    FEMALE = "F"


class ExamType(str, Enum):
    MID = "mid"
    FINAL = "final"
    QUIZ = "quiz"
    HOMEWORK = "homework"


class GradeLevel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


@dataclass
class Student:
    name: str
    age: int
    gender: Gender
    class_name: str
    email: str
    phone: str
    address: str
    grade: str
    id: Optional[int] = None

    def __post_init__(self):
        if not (0 < self.age < 150):
            raise ValueError(f"年龄无效: {self.age}")
        if not self.name.strip():
            raise ValueError("姓名不能为空")
        if "@" not in self.email or "." not in self.email:
            raise ValueError(f"邮箱格式无效: {self.email}")


@dataclass
class Course:
    name: str
    teacher: str
    credits: int
    description: str = ""
    id: Optional[int] = None


@dataclass
class Score:
    student_id: int
    course_id: int
    score: float
    exam_type: ExamType
    date: str
    teacher: str
    comment: str = ""
    id: Optional[int] = None

    def __post_init__(self):
        if not (0 <= self.score <= 100):
            raise ValueError(f"分数超出范围: {self.score}")

    @property
    def grade_level(self) -> GradeLevel:
        if self.score >= 90:
            return GradeLevel.A
        elif self.score >= 80:
            return GradeLevel.B
        elif self.score >= 70:
            return GradeLevel.C
        elif self.score >= 60:
            return GradeLevel.D
        return GradeLevel.F

    @property
    def gpa_points(self) -> float:
        mapping = {
            GradeLevel.A: 4.0,
            GradeLevel.B: 3.0,
            GradeLevel.C: 2.0,
            GradeLevel.D: 1.0,
            GradeLevel.F: 0.0,
        }
        return mapping[self.grade_level]


@dataclass
class ClassStats:
    class_name: str
    student_count: int
    score_count: int
    average: float
    maximum: float
    minimum: float
    pass_count: int
    excellent_count: int

    @property
    def pass_rate(self) -> float:
        return self.pass_count / self.score_count * 100 if self.score_count else 0.0

    @property
    def excellent_rate(self) -> float:
        return self.excellent_count / self.score_count * 100 if self.score_count else 0.0
