"""
Enhanced Budget Planner with ML Integration
Combines traditional budget planning with AI-powered recommendations
"""

from flask import current_app
import uuid
from .ml_budget_generator import budget_generator
import logging

logger = logging.getLogger(__name__)

class EnhancedBudgetPlanner:
    """
    Enhanced budget planner that combines traditional planning with ML insights
    """
    
    def __init__(self):
        self.expense_categories = [
            'Housing', 'Utilities', 'Groceries', 'Transportation',
            'Healthcare', 'Insurance', 'Education', 'Savings',
            'Debt Payments', 'Personal Care', 'Entertainment',
            'Dining Out', 'Clothing', 'Gifts & Donations',
            'Travel', 'Childcare', 'Pets', 'Other'
        ]
    
    def create_smart_budget(self, user_id, budget_name="Smart Budget", use_ml=True):
        """
        Create a smart budget using ML if available, fallback to traditional methods
        """
        try:
            if use_ml and budget_generator.model_trained:
                logger.info(f"Creating ML-powered budget for user {user_id}")
                ml_budget = budget_generator.generate_budget_for_user(user_id)
                
                if ml_budget:
                    # Save ML budget to database
                    success = budget_generator.save_budget_to_database(ml_budget)
                    if success:
                        return {
                            'success': True,
                            'budget': ml_budget,
                            'method': 'ML',
                            'message': 'AI-powered budget created successfully'
                        }
                    else:
                        return {
                            'success': False,
                            'message': 'ML budget generated but failed to save to database'
                        }
            
            # Fallback to traditional budget creation
            logger.info(f"Creating traditional budget for user {user_id}")
            traditional_budget = self._create_traditional_budget(user_id, budget_name)
            
            if traditional_budget:
                return {
                    'success': True,
                    'budget': traditional_budget,
                    'method': 'Traditional',
                    'message': 'Traditional budget created successfully'
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to create budget using any method'
                }
                
        except Exception as e:
            logger.error(f"Error creating smart budget: {e}")
            return {
                'success': False,
                'message': f'Error creating budget: {str(e)}'
            }
    
    def _create_traditional_budget(self, user_id, budget_name):
        """
        Create budget using traditional percentage-based approach
        """
        try:
            user_data = self._get_user_expense_data(user_id)
            if not user_data:
                return None
            
            # Parse monthly income
            monthly_income = self._parse_monthly_income(user_data.get('monthly_income', '30000'))
            
            # Traditional budget percentages (50/30/20 rule modified)
            budget_percentages = {
                'Housing': 0.25,          # 25% for housing
                'Utilities': 0.08,        # 8% for utilities
                'Groceries': 0.12,        # 12% for groceries
                'Transportation': 0.10,   # 10% for transportation
                'Healthcare': 0.05,       # 5% for healthcare
                'Insurance': 0.03,        # 3% for insurance
                'Savings': 0.20,          # 20% for savings
                'Debt Payments': 0.05,    # 5% for debt payments
                'Entertainment': 0.05,    # 5% for entertainment
                'Dining Out': 0.04,       # 4% for dining out
                'Personal Care': 0.02,    # 2% for personal care
                'Clothing': 0.03,         # 3% for clothing
                'Other': 0.03             # 3% for other expenses
            }
            
            # Adjust based on user's actual data if available
            budget_percentages = self._adjust_percentages_based_on_data(
                budget_percentages, user_data, monthly_income
            )
            
            # Create budget structure
            budget = {
                'user_id': user_id,
                'name': budget_name,
                'monthly_income': monthly_income,
                'total_budget': 0,
                'categories': {}
            }
            
            # Calculate amounts for each category
            for category, percentage in budget_percentages.items():
                amount = monthly_income * percentage
                budget['categories'][category] = {
                    'amount': round(amount, 2),
                    'percentage': percentage * 100,
                    'items': self._generate_traditional_items(category, amount)
                }
                budget['total_budget'] += amount
            
            budget['total_budget'] = round(budget['total_budget'], 2)
            
            # Save to database
            if self._save_traditional_budget_to_db(budget):
                return budget
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating traditional budget: {e}")
            return None
    
    def _get_user_expense_data(self, user_id):
        """
        Get user expense habit data
        """
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT ueh.*, u.age, u.gender, u.marital_status
                    FROM user_expense_habit ueh
                    JOIN users u ON ueh.user_id = u.id
                    WHERE ueh.user_id = %s
                """, (user_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user expense data: {e}")
            return None
        finally:
            conn.close()
    
    def _parse_monthly_income(self, income_str):
        """
        Parse monthly income string to numeric value
        """
        if not income_str:
            return 30000  # Default
        
        income_str = str(income_str).lower()
        
        income_mapping = {
            'below 20000': 15000,
            '20000-40000': 30000,
            '40000-60000': 50000,
            '60000-80000': 70000,
            '80000-100000': 90000,
            'above 100000': 120000,
        }
        
        for range_key, value in income_mapping.items():
            if range_key in income_str:
                return value
        
        # Try to extract numeric value
        try:
            return float(''.join(filter(str.isdigit, income_str)))
        except:
            return 30000
    
    def _adjust_percentages_based_on_data(self, percentages, user_data, income):
        """
        Adjust budget percentages based on user's actual expense data
        """
        if not user_data:
            return percentages
        
        # Adjust housing based on actual rent
        if user_data.get('rent'):
            actual_housing_percentage = user_data['rent'] / income
            if 0.15 <= actual_housing_percentage <= 0.40:  # Reasonable range
                percentages['Housing'] = actual_housing_percentage
        
        # Adjust transportation based on actual cost
        if user_data.get('transport_cost'):
            actual_transport_percentage = user_data['transport_cost'] / income
            if 0.05 <= actual_transport_percentage <= 0.20:  # Reasonable range
                percentages['Transportation'] = actual_transport_percentage
        
        # Adjust groceries based on actual cost
        if user_data.get('grocery_cost'):
            actual_grocery_percentage = user_data['grocery_cost'] / income
            if 0.08 <= actual_grocery_percentage <= 0.25:  # Reasonable range
                percentages['Groceries'] = actual_grocery_percentage
        
        # Adjust utilities based on actual cost
        if user_data.get('utilities_cost'):
            actual_utilities_percentage = user_data['utilities_cost'] / income
            if 0.03 <= actual_utilities_percentage <= 0.15:  # Reasonable range
                percentages['Utilities'] = actual_utilities_percentage
        
        # Normalize percentages to ensure they don't exceed 100%
        total_percentage = sum(percentages.values())
        if total_percentage > 1.0:
            scale_factor = 0.95 / total_percentage  # Leave 5% buffer
            for category in percentages:
                percentages[category] *= scale_factor
        
        return percentages
    
    def _generate_traditional_items(self, category, total_amount):
        """
        Generate traditional budget items for each category
        """
        category_items = {
            'Housing': [
                {'name': 'Rent/Mortgage', 'amount': total_amount * 0.85},
                {'name': 'Property Tax', 'amount': total_amount * 0.10},
                {'name': 'Home Insurance', 'amount': total_amount * 0.05}
            ],
            'Utilities': [
                {'name': 'Electricity', 'amount': total_amount * 0.40},
                {'name': 'Water & Sewer', 'amount': total_amount * 0.25},
                {'name': 'Gas', 'amount': total_amount * 0.20},
                {'name': 'Internet/Cable', 'amount': total_amount * 0.15}
            ],
            'Transportation': [
                {'name': 'Fuel/Public Transport', 'amount': total_amount * 0.60},
                {'name': 'Vehicle Maintenance', 'amount': total_amount * 0.25},
                {'name': 'Insurance', 'amount': total_amount * 0.15}
            ],
            'Groceries': [
                {'name': 'Food & Beverages', 'amount': total_amount * 0.85},
                {'name': 'Household Supplies', 'amount': total_amount * 0.15}
            ]
        }
        
        # Default single item for categories not specified
        default_items = [{'name': f'{category} Expenses', 'amount': total_amount}]
        
        items = category_items.get(category, default_items)
        
        # Round amounts
        for item in items:
            item['amount'] = round(item['amount'], 2)
        
        return items
    
    def _save_traditional_budget_to_db(self, budget):
        """
        Save traditional budget to database
        """
        conn = current_app.get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Create main budget record
                budget_id = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO budgets (id, user_id, name, currency, amount, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 MONTH))
                """, (
                    budget_id,
                    budget['user_id'],
                    budget['name'],
                    'USD',
                    budget['total_budget']
                ))
                
                # Create category and item records
                for category_name, category_data in budget['categories'].items():
                    category_id = str(uuid.uuid4())
                    
                    cursor.execute("""
                        INSERT INTO budget_expense_categories (id, budget_id, category_name, amount)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        category_id,
                        budget_id,
                        category_name,
                        category_data['amount']
                    ))
                    
                    # Create item records
                    for item in category_data['items']:
                        item_id = str(uuid.uuid4())
                        
                        cursor.execute("""
                            INSERT INTO budget_expense_items (id, category_id, name, amount, details)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            item_id,
                            category_id,
                            item['name'],
                            item['amount'],
                            'Traditional Budget Item'
                        ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error saving traditional budget: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_budget_comparison(self, user_id):
        """
        Compare ML budget vs Traditional budget for analysis
        """
        try:
            ml_budget = None
            traditional_budget = None
            
            # Try to generate both types
            if budget_generator.model_trained:
                ml_budget = budget_generator.generate_budget_for_user(user_id)
            
            traditional_budget = self._create_traditional_budget(user_id, "Comparison Budget")
            
            comparison = {
                'user_id': user_id,
                'ml_available': ml_budget is not None,
                'traditional_available': traditional_budget is not None,
                'comparison': {}
            }
            
            if ml_budget and traditional_budget:
                # Compare category by category
                all_categories = set(ml_budget['categories'].keys()) | set(traditional_budget['categories'].keys())
                
                for category in all_categories:
                    ml_amount = ml_budget['categories'].get(category, {}).get('amount', 0)
                    trad_amount = traditional_budget['categories'].get(category, {}).get('amount', 0)
                    
                    difference = ml_amount - trad_amount
                    percentage_diff = (difference / trad_amount * 100) if trad_amount > 0 else 0
                    
                    comparison['comparison'][category] = {
                        'ml_amount': ml_amount,
                        'traditional_amount': trad_amount,
                        'difference': difference,
                        'percentage_difference': round(percentage_diff, 2)
                    }
                
                comparison['total_difference'] = ml_budget['total_budget'] - traditional_budget['total_budget']
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error creating budget comparison: {e}")
            return None

# Create global instance
enhanced_budget_planner = EnhancedBudgetPlanner()