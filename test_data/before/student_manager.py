import sqlite3
import os
import sys
import json
import csv
import datetime
import hashlib
import random
import re
import math
from db_helper import get_connection, save_to_db
from utils import calc_avg, calc_avg2, format_name, format_name2


# 全局变量
DB = "students.db"
PASS = "admin123"
SECRET = "mysecretkey_hardcoded"
MAX = 100
MIN = 0
GRADE_LEVELS = ["A", "B", "C", "D", "F"]


class StudentSystem:
    """学生成绩管理系统 - 做所有事情的上帝类"""

    def __init__(self):
        self.conn = sqlite3.connect(DB)
        self.students = []
        self.grades = []
        self.teachers = []
        self.courses = []
        self.logged_in = False
        self.current_user = None
        self.log = []
        self.cache = {}
        self.tmp = []
        self.data = {}
        self.x = None
        self.y = None
        self.z = None

    def login(self, u, p):
        # 检查登录
        if u == "admin":
            if p == PASS:
                self.logged_in = True
                self.current_user = u
                return True
            else:
                return False
        else:
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            # SQL注入漏洞
            query = "SELECT * FROM users WHERE username='" + u + "' AND password='" + p + "'"
            cur.execute(query)
            row = cur.fetchone()
            if row:
                self.logged_in = True
                self.current_user = u
                return True
            else:
                return False

    def add_student(self, n, a, g, c, e, p, addr, grd):
        # 添加学生，参数太多，没有验证
        if n == None or n == "":
            print("name error")
            return False
        if a == None:
            print("age error")
            return False
        if a < 0 or a > 150:
            print("age range error")
            return False
        if g not in ["M", "F", "male", "female", "m", "f", "Male", "Female"]:
            print("gender error")
            return False
        if c == None or c == "":
            print("class error")
            return False
        if e == None or e == "":
            print("email error")
            return False
        # 没有验证邮箱格式
        if p == None or p == "":
            print("phone error")
            return False
        if addr == None or addr == "":
            print("address error")
            return False
        if grd == None or grd == "":
            print("grade error")
            return False

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        # 又一个SQL注入
        sql = "INSERT INTO students (name, age, gender, class, email, phone, address, grade) VALUES ('" + n + "', " + str(a) + ", '" + g + "', '" + c + "', '" + e + "', '" + p + "', '" + addr + "', '" + grd + "')"
        try:
            cur.execute(sql)
            conn.commit()
            self.log.append("added student: " + n)
            return True
        except Exception as ex:
            print("error: " + str(ex))
            return False

    def get_student(self, id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        # SQL注入
        sql = "SELECT * FROM students WHERE id=" + str(id)
        cur.execute(sql)
        return cur.fetchone()

    def update_student(self, id, n, a, g, c, e, p, addr, grd):
        if n == None or n == "":
            print("name error")
            return False
        if a == None:
            print("age error")
            return False
        if a < 0 or a > 150:
            print("age range error")
            return False
        if g not in ["M", "F", "male", "female", "m", "f", "Male", "Female"]:
            print("gender error")
            return False
        if c == None or c == "":
            print("class error")
            return False
        if e == None or e == "":
            print("email error")
            return False
        if p == None or p == "":
            print("phone error")
            return False
        if addr == None or addr == "":
            print("address error")
            return False
        if grd == None or grd == "":
            print("grade error")
            return False

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        # 重复的SQL注入
        sql = "UPDATE students SET name='" + n + "', age=" + str(a) + ", gender='" + g + "', class='" + c + "', email='" + e + "', phone='" + p + "', address='" + addr + "', grade='" + grd + "' WHERE id=" + str(id)
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as ex:
            print(ex)
            return False

    def delete_student(self, id):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        sql = "DELETE FROM students WHERE id=" + str(id)
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except:
            return False

    def add_score(self, sid, cid, score, exam_type, date, teacher, comment):
        # 验证逻辑复制粘贴
        if sid == None:
            return False
        if cid == None:
            return False
        if score == None:
            return False
        if score < 0:
            print("score < 0")
            return False
        if score > 100:
            print("score > 100")
            return False
        if exam_type not in ["mid", "final", "quiz", "homework"]:
            print("bad exam type")
            return False
        if date == None or date == "":
            return False
        if teacher == None or teacher == "":
            return False

        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        sql = "INSERT INTO scores (student_id, course_id, score, exam_type, date, teacher, comment) VALUES (" + str(sid) + ", " + str(cid) + ", " + str(score) + ", '" + exam_type + "', '" + date + "', '" + teacher + "', '" + comment + "')"
        try:
            cur.execute(sql)
            conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def calc_gpa(self, sid):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        sql = "SELECT score FROM scores WHERE student_id=" + str(sid)
        cur.execute(sql)
        rows = cur.fetchall()
        if rows == None or len(rows) == 0:
            return 0
        total = 0
        cnt = 0
        for r in rows:
            s = r[0]
            if s >= 90:
                gp = 4.0
            else:
                if s >= 80:
                    gp = 3.0
                else:
                    if s >= 70:
                        gp = 2.0
                    else:
                        if s >= 60:
                            gp = 1.0
                        else:
                            if s >= 0:
                                gp = 0.0
                            else:
                                gp = 0.0
            total = total + gp
            cnt = cnt + 1
        if cnt == 0:
            return 0
        return total / cnt

    def get_rank(self, sid, cid):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        sql = "SELECT score FROM scores WHERE student_id=" + str(sid) + " AND course_id=" + str(cid)
        cur.execute(sql)
        my_score_row = cur.fetchone()
        if my_score_row == None:
            return -1
        my_score = my_score_row[0]

        sql2 = "SELECT score FROM scores WHERE course_id=" + str(cid)
        cur.execute(sql2)
        all_scores = cur.fetchall()

        rank = 1
        for row in all_scores:
            s = row[0]
            if s > my_score:
                rank = rank + 1
        return rank

    def generate_report(self, sid, format_type, output_path, include_chart, include_comments, show_rank, show_gpa, lang):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        sql = "SELECT * FROM students WHERE id=" + str(sid)
        cur.execute(sql)
        student = cur.fetchone()
        if student == None:
            print("student not found")
            return False

        sql2 = "SELECT s.score, c.name, s.exam_type, s.date FROM scores s JOIN courses c ON s.course_id=c.id WHERE s.student_id=" + str(sid)
        cur.execute(sql2)
        scores = cur.fetchall()

        if format_type == "txt":
            content = ""
            if lang == "cn":
                content += "学生报告\n"
                content += "========\n"
                content += "姓名: " + str(student[1]) + "\n"
                content += "年龄: " + str(student[2]) + "\n"
                content += "班级: " + str(student[4]) + "\n"
                if show_gpa:
                    gpa = self.calc_gpa(sid)
                    content += "GPA: " + str(gpa) + "\n"
                content += "\n成绩列表:\n"
                for sc in scores:
                    content += "  " + str(sc[1]) + ": " + str(sc[0])
                    if show_rank:
                        # 这里应该传cid但是没有
                        content += " (排名: N/A)"
                    if include_comments and sc[2]:
                        content += " [" + sc[2] + "]"
                    content += "\n"
            else:
                content += "Student Report\n"
                content += "==============\n"
                content += "Name: " + str(student[1]) + "\n"
                content += "Age: " + str(student[2]) + "\n"
                content += "Class: " + str(student[4]) + "\n"
                if show_gpa:
                    gpa = self.calc_gpa(sid)
                    content += "GPA: " + str(gpa) + "\n"
                content += "\nScores:\n"
                for sc in scores:
                    content += "  " + str(sc[1]) + ": " + str(sc[0])
                    if show_rank:
                        content += " (Rank: N/A)"
                    if include_comments and sc[2]:
                        content += " [" + sc[2] + "]"
                    content += "\n"

            f = open(output_path, "w")
            f.write(content)
            f.close()
            return True

        elif format_type == "csv":
            import csv
            f = open(output_path, "w")
            writer = csv.writer(f)
            if lang == "cn":
                writer.writerow(["课程", "分数", "考试类型", "日期"])
            else:
                writer.writerow(["Course", "Score", "Exam Type", "Date"])
            for sc in scores:
                writer.writerow([sc[1], sc[0], sc[2], sc[3]])
            f.close()
            return True

        elif format_type == "json":
            data = {}
            data["name"] = student[1]
            data["age"] = student[2]
            data["scores"] = []
            for sc in scores:
                item = {}
                item["course"] = sc[1]
                item["score"] = sc[0]
                item["type"] = sc[2]
                item["date"] = sc[3]
                data["scores"].append(item)
            if show_gpa:
                data["gpa"] = self.calc_gpa(sid)
            f = open(output_path, "w")
            json.dump(data, f)
            f.close()
            return True
        else:
            print("unknown format")
            return False

    def search_students(self, keyword, field, min_score, max_score, grade, class_name, gender, sort_by, order):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        # 拼接SQL
        sql = "SELECT * FROM students WHERE 1=1"
        if keyword != None and keyword != "":
            sql += " AND " + field + " LIKE '%" + keyword + "%'"
        if grade != None and grade != "":
            sql += " AND grade='" + grade + "'"
        if class_name != None and class_name != "":
            sql += " AND class='" + class_name + "'"
        if gender != None and gender != "":
            sql += " AND gender='" + gender + "'"
        if sort_by != None:
            sql += " ORDER BY " + sort_by
            if order == "desc":
                sql += " DESC"
        cur.execute(sql)
        students = cur.fetchall()

        result = []
        for s in students:
            if min_score != None or max_score != None:
                avg = calc_avg(s[0])
                if min_score != None and avg < min_score:
                    continue
                if max_score != None and avg > max_score:
                    continue
            result.append(s)
        return result

    def bulk_import(self, filepath):
        if filepath == None or filepath == "":
            return 0
        if not os.path.exists(filepath):
            print("file not found: " + filepath)
            return 0

        count = 0
        errors = 0
        f = open(filepath, "r")
        for line in f:
            line = line.strip()
            if line == "":
                continue
            parts = line.split(",")
            if len(parts) < 8:
                errors += 1
                continue
            n = parts[0]
            try:
                a = int(parts[1])
            except:
                errors += 1
                continue
            g = parts[2]
            c = parts[3]
            e = parts[4]
            p = parts[5]
            addr = parts[6]
            grd = parts[7]

            ok = self.add_student(n, a, g, c, e, p, addr, grd)
            if ok:
                count += 1
            else:
                errors += 1
        f.close()
        print("imported: " + str(count) + ", errors: " + str(errors))
        return count

    def get_statistics(self, class_name, course_id, year):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        if class_name != None:
            sql = "SELECT s.id FROM students s WHERE s.class='" + class_name + "'"
        else:
            sql = "SELECT s.id FROM students s"
        cur.execute(sql)
        student_ids = [r[0] for r in cur.fetchall()]

        if len(student_ids) == 0:
            return {}

        scores_list = []
        for sid in student_ids:
            if course_id != None:
                sql2 = "SELECT score FROM scores WHERE student_id=" + str(sid) + " AND course_id=" + str(course_id)
            else:
                sql2 = "SELECT score FROM scores WHERE student_id=" + str(sid)
            if year != None:
                sql2 += " AND date LIKE '" + str(year) + "%'"
            cur.execute(sql2)
            for r in cur.fetchall():
                scores_list.append(r[0])

        if len(scores_list) == 0:
            return {"count": 0}

        total = 0
        for s in scores_list:
            total += s
        avg = total / len(scores_list)

        mx = scores_list[0]
        mn = scores_list[0]
        for s in scores_list:
            if s > mx:
                mx = s
            if s < mn:
                mn = s

        passed = 0
        failed = 0
        excellent = 0
        for s in scores_list:
            if s >= 90:
                excellent += 1
            if s >= 60:
                passed += 1
            else:
                failed += 1

        return {
            "count": len(scores_list),
            "avg": avg,
            "max": mx,
            "min": mn,
            "passed": passed,
            "failed": failed,
            "excellent": excellent,
            "pass_rate": passed / len(scores_list) * 100
        }
