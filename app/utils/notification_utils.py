import uuid
from datetime import datetime
from flask import current_app
import pymysql

def create_notification(user_id, message, link=None):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO notifications (id, user_id, message, is_read, created_at, link)
                VALUES (%s, %s, %s, 0, %s, %s)
            """
            cursor.execute(sql, (str(uuid.uuid4()), user_id, message, datetime.now(), link))
        conn.commit()
    finally:
        conn.close()

def get_unread_notifications(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM notifications WHERE user_id = %s AND is_read = 0 ORDER BY created_at DESC"
            cursor.execute(sql, (user_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def mark_notifications_read(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE notifications SET is_read = 1 WHERE user_id = %s"
            cursor.execute(sql, (user_id,))
        conn.commit()
    finally:
        conn.close()

def get_recent_notifications(user_id, limit=10):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC LIMIT %s"
            cursor.execute(sql, (user_id, limit))
            return cursor.fetchall()
    finally:
        conn.close()