# Utility functions for user expense habit
from flask import current_app
import uuid

def get_expense_habit(user_id):
    conn = current_app.get_db_connection()
    habit = conn.execute('SELECT * FROM user_expense_habit WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return habit

def upsert_expense_habit(user_id, data):
    conn = current_app.get_db_connection()
    habit = conn.execute('SELECT * FROM user_expense_habit WHERE user_id = ?', (user_id,)).fetchone()
    if habit:
        conn.execute('''UPDATE user_expense_habit SET monthly_income=?, earning_member=?, dependents=?, living_situation=?, rent=?, transport_mode=?, transport_cost=?, eating_out_frequency=?, grocery_cost=?, utilities_cost=?, mobile_internet_cost=?, subscriptions=?, savings=?, investments=?, loans=?, loan_payment=?, financial_goal=? WHERE id=?''',
            (data['monthly_income'], data['earning_member'], data['dependents'], data['living_situation'], data['rent'], data['transport_mode'], data['transport_cost'], data['eating_out_frequency'], data['grocery_cost'], data['utilities_cost'], data['mobile_internet_cost'], data['subscriptions'], data['savings'], data['investments'], data['loans'], data['loan_payment'], data['financial_goal'], habit['id']))
    else:
        conn.execute('''INSERT INTO user_expense_habit (id, user_id, timestamp, monthly_income, earning_member, dependents, living_situation, rent, transport_mode, transport_cost, eating_out_frequency, grocery_cost, utilities_cost, mobile_internet_cost, subscriptions, savings, investments, loans, loan_payment, financial_goal) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (str(uuid.uuid4()), user_id, data['monthly_income'], data['earning_member'], data['dependents'], data['living_situation'], data['rent'], data['transport_mode'], data['transport_cost'], data['eating_out_frequency'], data['grocery_cost'], data['utilities_cost'], data['mobile_internet_cost'], data['subscriptions'], data['savings'], data['investments'], data['loans'], data['loan_payment'], data['financial_goal']))
    conn.commit()
    habit = conn.execute('SELECT * FROM user_expense_habit WHERE user_id = ?', (user_id,)).fetchone()
    conn.close()
    return habit
