
from flask import current_app
import uuid

def get_expense_habit(user_id):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user_expense_habit WHERE user_id = %s', (user_id,))
            habit = cursor.fetchone()
        return habit
    finally:
        conn.close()

def upsert_expense_habit(user_id, data):
    conn = current_app.get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM user_expense_habit WHERE user_id = %s', (user_id,))
            habit = cursor.fetchone()
            
            if habit:
                cursor.execute('''UPDATE user_expense_habit SET monthly_income=%s, earning_member=%s, dependents=%s, living_situation=%s, rent=%s, transport_mode=%s, transport_cost=%s, eating_out_frequency=%s, grocery_cost=%s, utilities_cost=%s, mobile_internet_cost=%s, subscriptions=%s, savings=%s, investments=%s, loans=%s, loan_payment=%s, financial_goal=%s WHERE id=%s''',
                    (data['monthly_income'], data['earning_member'], data['dependents'], data['living_situation'], data['rent'], data['transport_mode'], data['transport_cost'], data['eating_out_frequency'], data['grocery_cost'], data['utilities_cost'], data['mobile_internet_cost'], data['subscriptions'], data['savings'], data['investments'], data['loans'], data['loan_payment'], data['financial_goal'], habit['id']))
            else:
                cursor.execute('''INSERT INTO user_expense_habit (id, user_id, timestamp, monthly_income, earning_member, dependents, living_situation, rent, transport_mode, transport_cost, eating_out_frequency, grocery_cost, utilities_cost, mobile_internet_cost, subscriptions, savings, investments, loans, loan_payment, financial_goal) VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                    (str(uuid.uuid4()), user_id, data['monthly_income'], data['earning_member'], data['dependents'], data['living_situation'], data['rent'], data['transport_mode'], data['transport_cost'], data['eating_out_frequency'], data['grocery_cost'], data['utilities_cost'], data['mobile_internet_cost'], data['subscriptions'], data['savings'], data['investments'], data['loans'], data['loan_payment'], data['financial_goal']))
            
            conn.commit()
            cursor.execute('SELECT * FROM user_expense_habit WHERE user_id = %s', (user_id,))
            habit = cursor.fetchone()
        return habit
    finally:
        conn.close()
