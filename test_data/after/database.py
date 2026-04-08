import os
import sqlite3
import hashlib
import secrets
from contextlib import contextmanager
from typing import Any, Optional

DB_PATH = os.environ.get("SCHOOL_DB_PATH", "school.db")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    salt, digest = stored_hash.split(":", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == digest


def authenticate_user(username: str, password: str) -> Optional[dict]:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row and verify_password(password, row["password_hash"]):
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None


def create_tables():
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                age     INTEGER NOT NULL,
                gender  TEXT    NOT NULL,
                class   TEXT    NOT NULL,
                email   TEXT    NOT NULL UNIQUE,
                phone   TEXT    NOT NULL,
                address TEXT    NOT NULL,
                grade   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS courses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                teacher     TEXT    NOT NULL,
                credits     INTEGER NOT NULL,
                description TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS scores (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL REFERENCES students(id),
                course_id  INTEGER NOT NULL REFERENCES courses(id),
                score      REAL    NOT NULL,
                exam_type  TEXT    NOT NULL,
                date       TEXT    NOT NULL,
                teacher    TEXT    NOT NULL,
                comment    TEXT    DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role          TEXT NOT NULL DEFAULT 'user'
            );
        """)
        default_hash = hash_password(os.environ.get("ADMIN_PASSWORD", "changeme"))
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            ("admin", default_hash, "admin"),
        )
