import sqlite3
import os
import sys
import math
import json
import csv
import datetime
import random
import re
import hashlib  # 未使用
import collections  # 未使用
import itertools  # 未使用


DB = "students.db"


# 和student_manager.py中重复的全局常量
MAX_SCORE = 100
MIN_SCORE = 0
PASS_SCORE = 60
EXCELLENT_SCORE = 90
GRADE_LEVELS = ["A", "B", "C", "D", "F"]  # 重复定义


def calc_avg(student_id):
    """计算学生平均分 - 和student_manager中的逻辑重复"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    sql = "SELECT score FROM scores WHERE student_id=" + str(student_id)
    cur.execute(sql)
    rows = cur.fetchall()
    if not rows:
        return 0
    total = 0
    for r in rows:
        total = total + r[0]
    return total / len(rows)


def calc_avg2(student_id, course_id):
    """带课程ID的平均分 - 几乎和calc_avg一样"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    sql = "SELECT score FROM scores WHERE student_id=" + str(student_id) + " AND course_id=" + str(course_id)
    cur.execute(sql)
    rows = cur.fetchall()
    if not rows:
        return 0
    total = 0
    for r in rows:
        total = total + r[0]
    return total / len(rows)


def calc_avg3(scores_list):
    """从列表计算平均分 - 第三个重复的平均计算"""
    if scores_list == None or len(scores_list) == 0:
        return 0
    total = 0
    n = 0
    for s in scores_list:
        total = total + s
        n = n + 1
    return total / n


def format_name(n):
    """格式化名字"""
    if n == None:
        return ""
    n = n.strip()
    if n == "":
        return ""
    return n[0].upper() + n[1:].lower()


def format_name2(first, last):
    """格式化全名 - 重复的格式化逻辑"""
    if first == None:
        first = ""
    if last == None:
        last = ""
    first = first.strip()
    last = last.strip()
    if first == "" and last == "":
        return ""
    f = first[0].upper() + first[1:].lower() if first else ""
    l = last[0].upper() + last[1:].lower() if last else ""
    return f + " " + l


def score_to_grade(s):
    """分数转等级"""
    if s == None:
        return "N/A"
    if s >= 90:
        return "A"
    else:
        if s >= 80:
            return "B"
        else:
            if s >= 70:
                return "C"
            else:
                if s >= 60:
                    return "D"
                else:
                    if s >= 0:
                        return "F"
                    else:
                        return "N/A"


def score_to_grade2(score):
    """另一个分数转等级函数 - 几乎完全一样"""
    if score is None:
        return "未知"
    if score >= 90:
        grade = "优秀"
    else:
        if score >= 80:
            grade = "良好"
        else:
            if score >= 70:
                grade = "中等"
            else:
                if score >= 60:
                    grade = "及格"
                else:
                    grade = "不及格"
    return grade


def validate_email(email):
    """验证邮箱"""
    if email == None or email == "":
        return False
    # 简单检查
    if "@" in email and "." in email:
        return True
    return False


def validate_phone(phone):
    """验证手机号"""
    if phone == None or phone == "":
        return False
    phone = str(phone).strip()
    if len(phone) == 11:
        return True
    return False


def validate_email2(e):
    """重复的邮箱验证 - 几乎和validate_email一样"""
    if e == None:
        return False
    if e == "":
        return False
    if "@" in e:
        if "." in e:
            return True
    return False


def get_student_summary(sid):
    """获取学生摘要"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # SQL注入
    sql = "SELECT * FROM students WHERE id=" + str(sid)
    cur.execute(sql)
    s = cur.fetchone()
    if s == None:
        return None

    avg = calc_avg(sid)
    grade = score_to_grade(avg)

    return {
        "id": s[0],
        "name": s[1],
        "avg": avg,
        "grade": grade
    }


def get_class_summary(class_name):
    """获取班级摘要 - 和student_manager中的统计逻辑重复"""
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    sql = "SELECT id FROM students WHERE class='" + class_name + "'"
    cur.execute(sql)
    ids = [r[0] for r in cur.fetchall()]

    if len(ids) == 0:
        return {}

    all_scores = []
    for sid in ids:
        cur.execute("SELECT score FROM scores WHERE student_id=" + str(sid))
        for r in cur.fetchall():
            all_scores.append(r[0])

    if len(all_scores) == 0:
        return {"class": class_name, "count": len(ids), "avg": 0}

    total = 0
    for sc in all_scores:
        total += sc
    avg = total / len(all_scores)

    return {
        "class": class_name,
        "student_count": len(ids),
        "score_count": len(all_scores),
        "avg": avg
    }


def print_table(headers, rows):
    """打印表格"""
    # 计算每列宽度
    widths = []
    for i, h in enumerate(headers):
        w = len(str(h))
        for r in rows:
            if i < len(r):
                w = max(w, len(str(r[i])))
        widths.append(w)

    # 打印头部
    header_line = ""
    for i, h in enumerate(headers):
        header_line += str(h).ljust(widths[i] + 2)
    print(header_line)
    print("-" * len(header_line))

    # 打印行
    for r in rows:
        line = ""
        for i in range(len(headers)):
            if i < len(r):
                line += str(r[i]).ljust(widths[i] + 2)
            else:
                line += "".ljust(widths[i] + 2)
        print(line)


def print_table2(data_list, columns):
    """另一个打印表格函数 - 重复实现"""
    if not data_list:
        print("(empty)")
        return

    col_widths = {c: len(c) for c in columns}
    for item in data_list:
        for c in columns:
            v = str(item.get(c, ""))
            if len(v) > col_widths[c]:
                col_widths[c] = len(v)

    header = " | ".join(c.ljust(col_widths[c]) for c in columns)
    print(header)
    print("-" * len(header))
    for item in data_list:
        row = " | ".join(str(item.get(c, "")).ljust(col_widths[c]) for c in columns)
        print(row)


def export_csv(data, filepath, headers):
    """导出CSV"""
    f = open(filepath, "w", newline="")
    writer = csv.writer(f)
    writer.writerow(headers)
    for row in data:
        writer.writerow(row)
    f.close()


def export_csv2(data_list, filepath, columns):
    """重复的CSV导出"""
    f = open(filepath, "w", newline="")
    writer = csv.writer(f)
    writer.writerow(columns)
    for item in data_list:
        row = [item.get(c, "") for c in columns]
        writer.writerow(row)
    f.close()


def get_current_semester():
    """获取当前学期"""
    now = datetime.datetime.now()
    y = now.year
    m = now.month
    if m >= 9 or m <= 1:
        return str(y) + "-" + str(y + 1) + " 上学期"
    else:
        return str(y - 1) + "-" + str(y) + " 下学期"


# 未使用的死代码
def _old_calc_avg(sid):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT AVG(score) FROM scores WHERE student_id=?", (sid,))
    r = cur.fetchone()
    return r[0] if r and r[0] else 0


def _unused_helper(x, y, z):
    result = x * y + z
    tmp = result / 2
    final = tmp + x
    return final
