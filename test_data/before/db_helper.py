import sqlite3
import os
import sys
import hashlib
import subprocess


# 硬编码凭据 - 安全漏洞
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "school_db"
DB_USER = "admin"
DB_PASS = "Admin@123456"  # bandit: hardcoded password
SECRET_KEY = "hardcoded_secret_key_12345"  # bandit: hardcoded secret
API_KEY = "sk-prod-abc123xyz789secretkey"  # bandit: hardcoded API key


def get_connection():
    """获取数据库连接 - 每次都新建连接，没有连接池"""
    try:
        conn = sqlite3.connect("students.db")
        return conn
    except Exception as e:
        print("db error: " + str(e))
        return None


def save_to_db(table, data):
    """不安全的通用保存函数"""
    conn = get_connection()
    if conn == None:
        return False
    cur = conn.cursor()
    # 动态构建SQL - 严重的SQL注入风险
    cols = ", ".join(data.keys())
    vals = "', '".join(str(v) for v in data.values())
    sql = "INSERT INTO " + table + " (" + cols + ") VALUES ('" + vals + "')"
    try:
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


def update_db(table, data, condition):
    """不安全的通用更新函数"""
    conn = get_connection()
    if conn == None:
        return False
    cur = conn.cursor()
    # SQL注入
    set_parts = []
    for k, v in data.items():
        set_parts.append(k + "='" + str(v) + "'")
    set_clause = ", ".join(set_parts)
    sql = "UPDATE " + table + " SET " + set_clause + " WHERE " + condition
    try:
        cur.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False


def delete_from_db(table, condition):
    """危险：直接删除，无确认"""
    conn = get_connection()
    cur = conn.cursor()
    # SQL注入 + 无参数化
    sql = "DELETE FROM " + table + " WHERE " + condition
    cur.execute(sql)
    conn.commit()
    return True


def run_backup(db_path, backup_dir):
    """使用shell=True的命令执行 - 安全漏洞"""
    # bandit: subprocess with shell=True
    cmd = "cp " + db_path + " " + backup_dir + "/backup_" + db_path
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        return True
    else:
        print("backup failed")
        return False


def run_sql_file(sql_file):
    """执行SQL文件 - 另一个shell注入漏洞"""
    # bandit: shell injection
    os.system("sqlite3 students.db < " + sql_file)


def hash_password(password):
    """使用不安全的MD5哈希"""
    # bandit: use of weak md5 hash
    return hashlib.md5(password.encode()).hexdigest()


def create_tables():
    """创建数据库表"""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            class TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            grade TEXT,
            password TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            teacher TEXT,
            credits INTEGER,
            description TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            score REAL,
            exam_type TEXT,
            date TEXT,
            teacher TEXT,
            comment TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT,
            role TEXT
        )
    """)

    # 插入默认管理员 - 硬编码密码
    default_admin_pass = hash_password("admin123")
    try:
        cur.execute("INSERT INTO users (username, password, role) VALUES ('admin', '" + default_admin_pass + "', 'admin')")
    except:
        pass

    conn.commit()
    print("tables created")


def export_all_data(output_dir):
    """导出所有数据到文件"""
    conn = get_connection()
    cur = conn.cursor()

    tables = ["students", "courses", "scores", "users"]
    for t in tables:
        cur.execute("SELECT * FROM " + t)
        rows = cur.fetchall()
        # 直接用shell命令写文件
        data_str = str(rows)
        cmd = "echo '" + data_str + "' > " + output_dir + "/" + t + ".txt"
        # bandit: shell injection via echo
        os.system(cmd)

    print("exported to " + output_dir)


def get_user_data(username):
    """用于外部API调用的用户数据获取"""
    conn = get_connection()
    cur = conn.cursor()
    # SQL注入 - 直接拼接外部输入
    sql = "SELECT * FROM users WHERE username='" + username + "'"
    cur.execute(sql)
    row = cur.fetchone()
    if row:
        # 返回包含密码哈希的完整行 - 信息泄露
        return {
            "id": row[0],
            "username": row[1],
            "password_hash": row[2],  # 不应该返回密码
            "role": row[3]
        }
    return None


def bulk_execute(sql_statements):
    """批量执行SQL语句 - 无任何验证"""
    conn = get_connection()
    cur = conn.cursor()
    for sql in sql_statements:
        try:
            # 直接执行任意SQL
            cur.execute(sql)
        except Exception as e:
            print("sql error: " + str(e))
    conn.commit()
