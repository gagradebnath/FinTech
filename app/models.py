# ORM models for reference only. Not used by the app; all queries use sqlite3 directly.
# Uncomment the following lines and install flask_sqlalchemy if you want to use ORM:
# from flask_sqlalchemy import SQLAlchemy
# db = SQLAlchemy()
from datetime import date, datetime

# Example SQLAlchemy models for the FinGuard schema:

# class Role(db.Model):
#     __tablename__ = 'roles'
#     id = db.Column(db.String, primary_key=True)
#     name = db.Column(db.String)
#     description = db.Column(db.Text)
#     users = db.relationship('User', backref='role', lazy=True)

# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.String, primary_key=True)
#     first_name = db.Column(db.String)
#     last_name = db.Column(db.String)
#     dob = db.Column(db.Date)
#     age = db.Column(db.Integer)
#     gender = db.Column(db.String)
#     marital_status = db.Column(db.String)
#     blood_group = db.Column(db.String)
#     balance = db.Column(db.Float)
#     joining_date = db.Column(db.Date)
#     role_id = db.Column(db.String, db.ForeignKey('roles.id'))
#     contact_info = db.relationship('ContactInfo', backref='user', uselist=False)
#     budgets = db.relationship('Budget', backref='user', lazy=True)

# class ContactInfo(db.Model):
#     __tablename__ = 'contact_info'
#     id = db.Column(db.String, primary_key=True)
#     user_id = db.Column(db.String, db.ForeignKey('users.id'), unique=True)
#     email = db.Column(db.String, unique=True)
#     phone = db.Column(db.String)
#     address_id = db.Column(db.String, db.ForeignKey('addresses.id'))

# class Address(db.Model):
#     __tablename__ = 'addresses'
#     id = db.Column(db.String, primary_key=True)
#     country = db.Column(db.String)
#     division = db.Column(db.String)
#     district = db.Column(db.String)
#     area = db.Column(db.String)
#     contact_infos = db.relationship('ContactInfo', backref='address', lazy=True)

# class Budget(db.Model):
#     __tablename__ = 'budgets'
#     id = db.Column(db.String, primary_key=True)
#     user_id = db.Column(db.String, db.ForeignKey('users.id'))
#     name = db.Column(db.String)
#     currency = db.Column(db.String)
#     income_source = db.Column(db.String)
#     amount = db.Column(db.Float)
#     expense_categories = db.relationship('BudgetExpenseCategory', backref='budget', lazy=True)

# class BudgetExpenseCategory(db.Model):
#     __tablename__ = 'budget_expense_categories'
#     id = db.Column(db.String, primary_key=True)
#     budget_id = db.Column(db.String, db.ForeignKey('budgets.id'))
#     category_name = db.Column(db.String)
#     amount = db.Column(db.Float)
#     items = db.relationship('BudgetExpenseItem', backref='category', lazy=True)

# class BudgetExpenseItem(db.Model):
#     __tablename__ = 'budget_expense_items'
#     id = db.Column(db.String, primary_key=True)
#     category_id = db.Column(db.String, db.ForeignKey('budget_expense_categories.id'))
#     name = db.Column(db.String)
#     amount = db.Column(db.Float)

# class Transaction(db.Model):
#     __tablename__ = 'transactions'
#     id = db.Column(db.String, primary_key=True)
#     amount = db.Column(db.Float)
#     payment_method = db.Column(db.String)
#     timestamp = db.Column(db.DateTime)
#     sender_id = db.Column(db.String, db.ForeignKey('users.id'))
#     receiver_id = db.Column(db.String, db.ForeignKey('users.id'))
#     note = db.Column(db.Text)
#     type = db.Column(db.String)
#     location = db.Column(db.String)

# class UserExpenseHabit(db.Model):
#     __tablename__ = 'user_expense_habit'
#     id = db.Column(db.String, primary_key=True)
#     user_id = db.Column(db.String, db.ForeignKey('users.id'))
#     timestamp = db.Column(db.DateTime)
#     monthly_income = db.Column(db.String)
#     earning_member = db.Column(db.Boolean)
#     dependents = db.Column(db.Integer)
#     living_situation = db.Column(db.String)
#     rent = db.Column(db.Float)
#     transport_mode = db.Column(db.String)
#     transport_cost = db.Column(db.Float)
#     eating_out_frequency = db.Column(db.String)
#     grocery_cost = db.Column(db.Float)
#     utilities_cost = db.Column(db.Float)
#     mobile_internet_cost = db.Column(db.Float)
#     subscriptions = db.Column(db.String)
#     savings = db.Column(db.String)
#     investments = db.Column(db.Text)
#     loans = db.Column(db.Boolean)
#     loan_payment = db.Column(db.Float)
#     financial_goal = db.Column(db.String)

# ...additional models for roles, permissions, fraud, blockchain, etc. can be added similarly...
# This file is for reference only. The app uses direct sqlite3 queries for all database operations.
