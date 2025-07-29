import uuid
from datetime import datetime
from flask import current_app
import pymysql

def create_agent_money_request(agent_id, admin_id, amount, note=None):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO agent_money_requests (id, agent_id, admin_id, amount, status, note, created_at, updated_at)
                VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s)
            """
            now = datetime.now()
            request_id = str(uuid.uuid4())
            cursor.execute(sql, (request_id, agent_id, admin_id, amount, note, now, now))
        conn.commit()
        return request_id
    finally:
        conn.close()

def get_agent_money_requests_for_admin(admin_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT r.*, u.first_name, u.last_name, u.id as agent_id, c.phone
                FROM agent_money_requests r
                JOIN users u ON r.agent_id = u.id
                LEFT JOIN contact_info c ON u.id = c.user_id
                WHERE (r.admin_id = %s )
                ORDER BY r.created_at DESC
            """
            cursor.execute(sql, (admin_id,))
            return cursor.fetchall()
    finally:
        conn.close()

def update_agent_money_request_status(request_id, admin_id, status, note=None):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE agent_money_requests
                SET status = %s, admin_id = %s, note = %s, updated_at = %s
                WHERE id = %s
            """
            now = datetime.now()
            cursor.execute(sql, (status, admin_id, note, now, request_id))
        conn.commit()
    finally:
        conn.close()

def get_pending_agent_money_request_count(admin_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT COUNT(*) as cnt
                FROM agent_money_requests
                WHERE (admin_id = %s OR admin_id IS NULL) AND status = 'pending'
            """
            cursor.execute(sql, (admin_id,))
            row = cursor.fetchone()
            return row['cnt'] if row else 0
    finally:
        conn.close()

def approve_agent_money_request(request_id, admin_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get request details
            cursor.execute("SELECT agent_id, amount FROM agent_money_requests WHERE id = %s AND status = 'pending'", (request_id,))
            req = cursor.fetchone()
            if not req:
                return False
            agent_id = req['agent_id']
            amount = req['amount']

            # Update agent balance
            cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, agent_id))

            # Mark request as approved
            cursor.execute("""
                UPDATE agent_money_requests
                SET status = 'approved', admin_id = %s, updated_at = NOW()
                WHERE id = %s
            """, (admin_id, request_id))
        conn.commit()
        return True
    finally:
        conn.close()

def create_user_cashout_request(user_id, agent_id, amount, note=None):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO user_cashout_requests (id, user_id, agent_id, amount, status, note, created_at, updated_at)
                VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s)
            """
            now = datetime.now()
            request_id = str(uuid.uuid4())
            cursor.execute(sql, (request_id, user_id, agent_id, amount, note, now, now))
        conn.commit()
        return request_id
    finally:
        conn.close()

def get_cashout_requests_for_agent(agent_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT r.*, u.first_name, u.last_name, u.id as user_id, c.phone
                FROM user_cashout_requests r
                JOIN users u ON r.user_id = u.id
                LEFT JOIN contact_info c ON u.id = c.user_id
                WHERE r.agent_id = %s
                ORDER BY r.created_at DESC
            """
            cursor.execute(sql, (agent_id,))
            return cursor.fetchall()
    finally:
        conn.close()
def approve_user_cashout_request(request_id, agent_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Get request details
            cursor.execute("SELECT user_id, amount FROM user_cashout_requests WHERE id = %s AND status = 'pending'", (request_id,))
            req = cursor.fetchone()
            if not req:
                return False
            user_id = req['user_id']
            amount = req['amount']

            # Update balances
            cursor.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, user_id))
            cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, agent_id))

            # Mark request as approved
            cursor.execute("""
                UPDATE user_cashout_requests
                SET status = 'approved', updated_at = NOW()
                WHERE id = %s
            """, (request_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def update_user_cashout_request_status(request_id, agent_id, status, note=None):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE user_cashout_requests
                SET status = %s, agent_id = %s, note = %s, updated_at = %s
                WHERE id = %s
            """
            now = datetime.now()
            cursor.execute(sql, (status, agent_id, note, now, request_id))
        conn.commit()
    finally:
        conn.close()

def get_agent_money_request_by_id(request_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM agent_money_requests WHERE id = %s"
            cursor.execute(sql, (request_id,))
            return cursor.fetchone()
    finally:
        conn.close()

def get_user_cashout_request_by_id(request_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM user_cashout_requests WHERE id = %s"
            cursor.execute(sql, (request_id,))
            return cursor.fetchone()
    finally:
        conn.close()