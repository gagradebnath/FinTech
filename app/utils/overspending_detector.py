
import re
import os
from datetime import datetime
from flask import current_app
import pymysql

# Expense category options matching the frontend
EXPENSE_CATEGORIES = [
    'Housing',
    'Utilities', 
    'Groceries',
    'Transportation',
    'Healthcare',
    'Insurance',
    'Education',
    'Savings',
    'Debt Payments',
    'Personal Care',
    'Entertainment',
    'Dining Out',
    'Clothing',
    'Gifts & Donations',
    'Travel',
    'Childcare',
    'Pets',
    'Other'
]

# Keywords mapping for expense categorization
CATEGORY_KEYWORDS = {
    'Housing': [
        'rent', 'mortgage', 'house', 'home', 'apartment', 'property', 'landlord',
        'hoa', 'homeowners', 'real estate', 'housing', 'lease', 'rental',
        'property tax', 'home insurance', 'maintenance', 'repair', 'utilities deposit'
    ],
    
    'Utilities': [
        'electricity', 'electric', 'gas', 'water', 'sewer', 'internet', 'wifi',
        'cable', 'phone', 'cell', 'mobile', 'utility', 'power', 'energy',
        'trash', 'garbage', 'waste', 'heating', 'cooling', 'broadband'
    ],
    
    'Groceries': [
        'grocery', 'groceries', 'supermarket', 'walmart', 'target', 'costco',
        'food', 'market', 'store', 'shopping', 'produce', 'organic',
        'whole foods', 'safeway', 'kroger', 'publix', 'aldi', 'trader joe'
    ],
    
    'Transportation': [
        'gas', 'fuel', 'gasoline', 'car', 'auto', 'vehicle', 'transport',
        'bus', 'train', 'subway', 'metro', 'taxi', 'uber', 'lyft',
        'parking', 'toll', 'car payment', 'auto insurance', 'maintenance',
        'repair', 'oil change', 'tires', 'registration', 'dmv'
    ],
    
    'Healthcare': [
        'doctor', 'medical', 'hospital', 'clinic', 'pharmacy', 'medicine',
        'prescription', 'dental', 'dentist', 'vision', 'glasses', 'contacts',
        'health', 'copay', 'deductible', 'surgery', 'therapy', 'checkup'
    ],
    
    'Insurance': [
        'insurance', 'premium', 'policy', 'coverage', 'life insurance',
        'health insurance', 'auto insurance', 'home insurance', 'disability',
        'liability', 'comprehensive', 'collision'
    ],
    
    'Education': [
        'tuition', 'school', 'college', 'university', 'education', 'student',
        'books', 'textbook', 'supplies', 'course', 'class', 'learning',
        'certification', 'training', 'workshop', 'seminar', 'online course'
    ],
    
    'Savings': [
        'savings', 'save', 'investment', 'invest', 'retirement', '401k',
        'ira', 'pension', 'emergency fund', 'nest egg', 'deposit'
    ],
    
    'Debt Payments': [
        'loan', 'debt', 'credit card', 'payment', 'installment', 'financing',
        'student loan', 'personal loan', 'car loan', 'mortgage payment',
        'minimum payment', 'interest', 'principal'
    ],
    
    'Personal Care': [
        'haircut', 'salon', 'barber', 'spa', 'massage', 'skincare', 'cosmetics',
        'makeup', 'personal care', 'hygiene', 'shampoo', 'soap', 'toothpaste',
        'gym', 'fitness', 'workout', 'membership', 'trainer'
    ],
    
    'Entertainment': [
        'movie', 'cinema', 'theater', 'concert', 'show', 'entertainment',
        'netflix', 'spotify', 'streaming', 'games', 'gaming', 'xbox',
        'playstation', 'nintendo', 'books', 'magazine', 'hobby'
    ],
    
    'Dining Out': [
        'restaurant', 'dining', 'food delivery', 'takeout', 'fast food',
        'coffee', 'starbucks', 'cafe', 'bar', 'pub', 'lunch', 'dinner',
        'breakfast', 'mcdonald', 'burger', 'pizza', 'doordash', 'ubereats'
    ],
    
    'Clothing': [
        'clothes', 'clothing', 'shirt', 'pants', 'dress', 'shoes', 'sneakers',
        'jacket', 'coat', 'jeans', 'fashion', 'accessories', 'jewelry',
        'watch', 'belt', 'hat', 'socks', 'underwear'
    ],
    
    'Gifts & Donations': [
        'gift', 'present', 'donation', 'charity', 'birthday', 'wedding',
        'holiday', 'christmas', 'valentine', 'anniversary', 'contribution',
        'tithe', 'offering', 'fundraiser'
    ],
    
    'Travel': [
        'travel', 'trip', 'vacation', 'flight', 'airline', 'hotel', 'airbnb',
        'booking', 'rental car', 'cruise', 'tour', 'luggage', 'passport',
        'visa', 'travel insurance', 'sightseeing'
    ],
    
    'Childcare': [
        'childcare', 'daycare', 'babysitter', 'nanny', 'school fees',
        'kids', 'children', 'child', 'baby', 'diapers', 'formula',
        'toys', 'playground', 'camp', 'activities'
    ],
    
    'Pets': [
        'pet', 'dog', 'cat', 'vet', 'veterinary', 'pet food', 'pet supplies',
        'grooming', 'pet insurance', 'toys', 'leash', 'collar', 'litter',
        'pet store', 'animal'
    ]
}

def get_mysql_config():
    """Get MySQL configuration from environment variables"""
    config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'port': int(os.environ.get('MYSQL_PORT', 3306)),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', 'g85a'),
        'database': os.environ.get('MYSQL_DATABASE', 'fin_guard'),
        'charset': 'utf8mb4'
    }
    return config

def categorize_expense(description):
    
    if not description or not isinstance(description, str):
        return 'Other'
    
    # Convert to lowercase for case-insensitive matching
    description_lower = description.lower()
    
    # Score each category based on keyword matches
    category_scores = {}
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            # Check for exact word match (using word boundaries)
            if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', description_lower):
                # Give higher score for longer, more specific keywords
                score += len(keyword.split())
        
        if score > 0:
            category_scores[category] = score
    
    # Return the category with the highest score
    if category_scores:
        best_category = max(category_scores, key=category_scores.get)
        return best_category
    
    return 'Other'


def get_category_budget(user_id, category_name):
    if not user_id or not category_name:
        return 0.0
    
    # Validate category name
    if category_name not in EXPENSE_CATEGORIES:
        return 0.0
    
    try:
        # Get database connection from Flask app
        connection = current_app.get_db_connection()
        
        with connection.cursor() as cursor:
            # Fixed SQL query (moved WHERE clause before ORDER BY)
            query = """
            SELECT
                t.sum as budget
            FROM
            (
                SELECT
                    b.user_id,
                    c.category_name,
                    COALESCE(SUM(i.amount), 0) as sum
                FROM
                    budgets b
                    LEFT JOIN budget_expense_categories c ON b.id = c.budget_id
                    LEFT JOIN budget_expense_items i ON c.id = i.category_id
                WHERE 
                    b.user_id = %s AND c.category_name = %s
                GROUP BY
                    b.user_id,
                    c.category_name
            ) t
            """
            
            # Execute query with parameters
            cursor.execute(query, (user_id, category_name))
            result = cursor.fetchone()
            
            if result and result[0] is not None:
                return float(result[0])
            else:
                return 0.0 
                
    except Exception as e:
        print(f"Error retrieving budget for user {user_id}, category {category_name}: {e}")
        return 0.0
    
    finally:
        if 'connection' in locals():
            connection.close()


def get_all_category_budgets(user_id):
    """
    Retrieves budget amounts for all categories for a specific user.
    
    Args:
        user_id (str): The user ID to get budgets for
        
    Returns:
        dict: Dictionary with category names as keys and budget amounts as values
        
    Example:
        >>> get_all_category_budgets('user')
        {'Housing': 1500.0, 'Groceries': 400.0, 'Transportation': 300.0, ...}
    """
    if not user_id:
        return {}
    
    budgets = {}
    
    try:
        # Get database connection from Flask app
        connection = current_app.get_db_connection()
        
        with connection.cursor() as cursor:
            # Query to get all category budgets for the user
            query = """
            SELECT
                c.category_name,
                COALESCE(SUM(i.amount), 0) as budget_amount
            FROM
                budgets b
                LEFT JOIN budget_expense_categories c ON b.id = c.budget_id
                LEFT JOIN budget_expense_items i ON c.id = i.category_id
            WHERE 
                b.user_id = %s
            GROUP BY
                c.category_name
            ORDER BY
                c.category_name
            """
            
            # Execute query
            cursor.execute(query, (user_id,))
            results = cursor.fetchall()
            
            # Convert results to dictionary
            for row in results:
                if row[0]:  # category_name is not None
                    budgets[row[0]] = float(row[1]) if row[1] is not None else 0.0
                    
    except Exception as e:
        print(f"Error retrieving all budgets for user {user_id}: {e}")
        return {}
    
    finally:
        if 'connection' in locals():
            connection.close()
    
    return budgets

def get_expense_till_now(user_id, category_name):
    """
    Returns the total expense for a given user and category for the current month.
    """
    if not user_id or not category_name:
        return 0.0

    try:
        connection = current_app.get_db_connection()
        with connection.cursor() as cursor:
            # Get the first day of the current month
            first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            # Query to sum expenses for the current month, matching category in note
            query = """
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions t
            WHERE t.sender_id IS NOT NULL
              AND t.sender_id = %s

              AND t.note LIKE %s
              AND t.timestamp >= %s
            """
            cursor.execute(query, (user_id, category_name + '%', first_day))
            result = cursor.fetchone()
            return float(result[0]) if result and result[0] is not None else 0.0
    except Exception as e:
        print(f"Error retrieving expenses for user {user_id}, category {category_name}: {e}")
        return 0.0
    finally:
        if 'connection' in locals():
            connection.close()

def detect_overspending(user_id, expense_description, expense_amount):
    # Categorize the expense
    category = categorize_expense(expense_description)
    
    # Get budget for the category
    budget = get_category_budget(user_id, category)-get_expense_till_now(user_id, category)
    
    # Calculate overspending
    is_overspending = expense_amount > budget if budget > 0 else False
    overspending_amount = max(0, expense_amount - budget) if budget > 0 else 0
    percentage_over = (overspending_amount / budget * 100) if budget > 0 else 0
    
    return {
        'category': category,
        'budget': budget,
        'expense_amount': expense_amount,
        'is_overspending': is_overspending,
        'overspending_amount': overspending_amount,
        'percentage_over': round(percentage_over, 2),
        'message': f"Expense categorized as '{category}'. " + 
                  (f"Over budget by ${overspending_amount:.2f} ({percentage_over:.1f}%)" if is_overspending 
                   else f"Within budget (${budget - expense_amount:.2f} remaining)" if budget > 0
                   else "No budget set for this category")
    }



