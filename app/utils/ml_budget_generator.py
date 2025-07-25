"""
Machine Learning Budget Generator for FinGuard
This module uses user expense habits to generate personalized budgets using ML models
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import uuid
from typing import Dict, List, Tuple, Optional
import pymysql
from flask import current_app
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expense categories as per your requirements
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

class BudgetMLGenerator:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.model_trained = False
        
    def prepare_data(self) -> pd.DataFrame:
        """
        Fetch and prepare data from user_expense_habit table
        """
        conn = current_app.get_db_connection()
        try:
            query = """
            SELECT 
                ueh.*,
                u.age,
                u.gender,
                u.marital_status,
                a.country,
                a.division,
                a.district
            FROM user_expense_habit ueh
            JOIN users u ON ueh.user_id = u.id
            LEFT JOIN contact_info ci ON u.id = ci.user_id
            LEFT JOIN addresses a ON ci.address_id = a.id
            WHERE ueh.monthly_income IS NOT NULL
            """
            
            # Fetch data manually since pandas has issues with PyMySQL
            with conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if not rows:
                    logger.warning("No data found in user_expense_habit table")
                    return pd.DataFrame()
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Create DataFrame
                df = pd.DataFrame(rows, columns=columns)
            
            # Data preprocessing
            df = self._preprocess_data(df)
            return df
            
        except Exception as e:
            logger.error(f"Error preparing data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the raw data for ML training
        """
        # Handle missing values and convert data types
        df = df.fillna({
            'rent': 0,
            'transport_cost': 0,
            'grocery_cost': 0,
            'utilities_cost': 0,
            'mobile_internet_cost': 0,
            'loan_payment': 0,
            'dependents': 0,
            'country': 'Unknown',
            'division': 'Unknown',
            'district': 'Unknown'
        })
        
        # Convert numeric columns
        numeric_columns = ['age', 'rent', 'transport_cost', 'grocery_cost', 'utilities_cost', 
                          'mobile_internet_cost', 'loan_payment', 'dependents']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any remaining NaN values in numeric columns
        df['age'] = df['age'].fillna(df['age'].median() if df['age'].notna().any() else 30)
        
        # Convert monthly income to numeric
        df['monthly_income_numeric'] = df['monthly_income'].apply(self._parse_income)
        
        # Create derived features
        df['total_fixed_expenses'] = (
            df['rent'] + df['utilities_cost'] + 
            df['mobile_internet_cost'] + df['loan_payment']
        )
        
        df['total_variable_expenses'] = (
            df['transport_cost'] + df['grocery_cost']
        )
        
        # Calculate income to expense ratio
        df['income_expense_ratio'] = df['monthly_income_numeric'] / (
            df['total_fixed_expenses'] + df['total_variable_expenses'] + 1
        )
        
        # Encode categorical variables
        categorical_columns = [
            'gender', 'marital_status', 'living_situation', 
            'transport_mode', 'eating_out_frequency', 'savings',
            'country', 'division', 'district'
        ]
        
        for col in categorical_columns:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[f'{col}_encoded'] = self.label_encoders[col].transform(df[col].astype(str))
        
        return df
    
    def _parse_income(self, income_str: str) -> float:
        """
        Parse income string to numeric value
        """
        if pd.isna(income_str):
            return 0
        
        income_str = str(income_str).lower()
        
        # Income ranges mapping
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
            return 30000  # Default median income
    
    def train_models(self) -> bool:
        """
        Train ML models for each expense category
        """
        df = self.prepare_data()
        
        if df.empty:
            logger.error("No data available for training")
            return False
        
        # Feature columns
        feature_columns = [
            'monthly_income_numeric', 'age', 'dependents', 'earning_member',
            'total_fixed_expenses', 'total_variable_expenses', 'income_expense_ratio'
        ]
        
        # Add encoded categorical features
        encoded_columns = [col for col in df.columns if col.endswith('_encoded')]
        feature_columns.extend(encoded_columns)
        
        # Filter existing columns
        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features]
        
        # Train models for each category
        category_mappings = self._create_category_mappings()
        
        for category in EXPENSE_CATEGORIES:
            try:
                # Create target variable for this category
                y = self._create_target_for_category(df, category, category_mappings)
                
                if len(y.unique()) < 2:  # Skip if not enough variance
                    continue
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                # Scale features
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)
                
                # Train model
                model = RandomForestRegressor(
                    n_estimators=100, 
                    random_state=42,
                    max_depth=10,
                    min_samples_split=5
                )
                model.fit(X_train_scaled, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test_scaled)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                logger.info(f"Model for {category}: MAE={mae:.2f}, R2={r2:.3f}")
                
                # Store model and scaler
                self.models[category] = model
                self.scalers[category] = scaler
                
            except Exception as e:
                logger.error(f"Error training model for {category}: {e}")
                continue
        
        self.model_trained = True
        self._save_models()
        return True
    
    def _create_category_mappings(self) -> Dict[str, str]:
        """
        Map database fields to expense categories
        """
        return {
            'Housing': 'rent',
            'Utilities': 'utilities_cost',
            'Groceries': 'grocery_cost',
            'Transportation': 'transport_cost',
            'Debt Payments': 'loan_payment',
            'Personal Care': 'mobile_internet_cost',  # Approximation
        }
    
    def _create_target_for_category(self, df: pd.DataFrame, category: str, mappings: Dict) -> pd.Series:
        """
        Create target variable for a specific expense category
        """
        if category in mappings and mappings[category] in df.columns:
            return df[mappings[category]]
        else:
            # For categories without direct mapping, create estimated values
            return self._estimate_category_expense(df, category)
    
    def _estimate_category_expense(self, df: pd.DataFrame, category: str) -> pd.Series:
        """
        Estimate expense for categories without direct data
        """
        income = df['monthly_income_numeric']
        
        # Percentage-based estimates
        category_percentages = {
            'Healthcare': 0.05,  # 5% of income
            'Insurance': 0.03,   # 3% of income
            'Education': 0.02,   # 2% of income
            'Savings': 0.10,     # 10% of income
            'Entertainment': 0.05, # 5% of income
            'Dining Out': 0.08,  # 8% of income
            'Clothing': 0.03,    # 3% of income
            'Gifts & Donations': 0.02, # 2% of income
            'Travel': 0.03,      # 3% of income
            'Childcare': 0.15 if df['dependents'].mean() > 0 else 0.0,
            'Pets': 0.02,        # 2% of income
            'Other': 0.05        # 5% of income
        }
        
        percentage = category_percentages.get(category, 0.05)
        return income * percentage
    
    def generate_budget_for_user(self, user_id: str) -> Optional[Dict]:
        """
        Generate a personalized budget for a specific user using trained ML models
        """
        # Always try to load models to ensure we have the latest trained models
        if not self.model_trained or not self.models:
            logger.info("Loading trained ML models...")
            self._load_models()
        
        if not self.model_trained or not self.models:
            logger.error("No trained models available! Please train models first.")
            return None
        
        logger.info(f"Using {len(self.models)} trained ML models for budget generation")
        
        user_data = self._get_user_data(user_id)
        if not user_data:
            logger.error(f"No data found for user {user_id}")
            return None
        
        # Prepare user features
        user_features = self._prepare_user_features(user_data)
        
        budget = {
            'user_id': user_id,
            'categories': {},
            'total_budget': 0,
            'monthly_income': user_data.get('monthly_income_numeric', 0)
        }
        
        # Generate predictions for each category using YOUR trained models
        models_used = 0
        fallback_used = 0
        
        for category in EXPENSE_CATEGORIES:
            if category in self.models:
                try:
                    model = self.models[category]
                    scaler = self.scalers[category]
                    
                    logger.info(f"Using trained ML model for {category}")
                    
                    # Scale features using your trained scaler
                    user_features_scaled = scaler.transform([user_features])
                    
                    # Predict using YOUR trained Random Forest model
                    predicted_amount = model.predict(user_features_scaled)[0]
                    predicted_amount = max(0, predicted_amount)  # Ensure non-negative
                    
                    budget['categories'][category] = {
                        'amount': round(predicted_amount, 2),
                        'items': self._generate_category_items(category, predicted_amount)
                    }
                    budget['total_budget'] += predicted_amount
                    models_used += 1
                    
                except Exception as e:
                    logger.error(f"Error predicting for category {category}: {e}")
                    # Fallback to percentage-based estimation
                    fallback_amount = self._fallback_category_amount(
                        user_data.get('monthly_income_numeric', 0), category
                    )
                    budget['categories'][category] = {
                        'amount': fallback_amount,
                        'items': self._generate_category_items(category, fallback_amount)
                    }
                    budget['total_budget'] += fallback_amount
                    fallback_used += 1
            else:
                # Category not in trained models, use fallback
                logger.warning(f"No trained model found for {category}, using fallback estimation")
                fallback_amount = self._fallback_category_amount(
                    user_data.get('monthly_income_numeric', 0), category
                )
                budget['categories'][category] = {
                    'amount': fallback_amount,
                    'items': self._generate_category_items(category, fallback_amount)
                }
                budget['total_budget'] += fallback_amount
                fallback_used += 1
        
        logger.info(f"Budget generation complete: {models_used} ML predictions, {fallback_used} fallback estimates")
        
        # Adjust budget to ensure it doesn't exceed income
        budget = self._adjust_budget_to_income(budget)
        
        return budget
    
    def _get_user_data(self, user_id: str) -> Optional[Dict]:
        """
        Get user data for budget generation
        """
        conn = current_app.get_db_connection()
        try:
            query = """
            SELECT 
                ueh.*,
                u.age,
                u.gender,
                u.marital_status,
                a.country,
                a.division,
                a.district
            FROM user_expense_habit ueh
            JOIN users u ON ueh.user_id = u.id
            LEFT JOIN contact_info ci ON u.id = ci.user_id
            LEFT JOIN addresses a ON ci.address_id = a.id
            WHERE ueh.user_id = %s
            """
            
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                
                if result:
                    # Convert to dictionary if not already
                    if isinstance(result, tuple):
                        columns = [desc[0] for desc in cursor.description]
                        result = dict(zip(columns, result))
                    
                    logger.info(f"Retrieved user data for user_id: {user_id}")
                    
                    # Preprocess single user data
                    result['monthly_income_numeric'] = self._parse_income(result.get('monthly_income'))
                    
                    # Convert numeric fields with safer conversion
                    numeric_fields = ['age', 'rent', 'transport_cost', 'grocery_cost', 
                                    'utilities_cost', 'mobile_internet_cost', 'loan_payment', 'dependents']
                    for field in numeric_fields:
                        if field in result and result[field] is not None:
                            try:
                                result[field] = float(result[field])
                            except (ValueError, TypeError):
                                logger.warning(f"Could not convert {field} to float for user {user_id}")
                                result[field] = 0.0
                        else:
                            result[field] = 0.0
                    
                    # Ensure boolean fields
                    if 'earning_member' in result:
                        result['earning_member'] = bool(result['earning_member'])
                    else:
                        result['earning_member'] = True
                    
                    return result
                    
                else:
                    logger.error(f"No data found for user_id: {user_id}")
                    return None
                
        except Exception as e:
            logger.error(f"Error getting user data for user_id {user_id}: {e}")
            return None
        finally:
            conn.close()
    
    def _prepare_user_features(self, user_data: Dict) -> List[float]:
        """
        Prepare feature vector for a single user
        """
        features = []
        
        # Numeric features
        features.extend([
            user_data.get('monthly_income_numeric', 0),
            user_data.get('age', 30),
            user_data.get('dependents', 0),
            1 if user_data.get('earning_member') else 0,
        ])
        
        # Calculate derived features
        total_fixed = (
            user_data.get('rent', 0) + user_data.get('utilities_cost', 0) +
            user_data.get('mobile_internet_cost', 0) + user_data.get('loan_payment', 0)
        )
        total_variable = user_data.get('transport_cost', 0) + user_data.get('grocery_cost', 0)
        income_expense_ratio = user_data.get('monthly_income_numeric', 0) / (total_fixed + total_variable + 1)
        expense_per_dependent = total_fixed / (user_data.get('dependents', 0) + 1)
        age_income_ratio = user_data.get('age', 30) / (user_data.get('monthly_income_numeric', 30000) / 1000)
        
        features.extend([total_fixed, total_variable, income_expense_ratio, 
                        expense_per_dependent, age_income_ratio])
        
        # Encoded categorical features
        categorical_columns = [
            'gender', 'marital_status', 'living_situation', 
            'transport_mode', 'eating_out_frequency', 'savings',
            'country', 'division', 'district'
        ]
        
        for col in categorical_columns:
            if col in self.label_encoders:
                try:
                    value = str(user_data.get(col, 'Unknown'))
                    encoded_value = self.label_encoders[col].transform([value])[0]
                    features.append(encoded_value)
                except:
                    features.append(0)  # Default value for unknown categories
            else:
                features.append(0)
        
        return features
    
    def _generate_category_items(self, category: str, total_amount: float) -> List[Dict]:
        """
        Generate specific items for each category
        """
        category_items = {
            'Housing': [
                {'name': 'Rent/Mortgage', 'amount': total_amount * 0.8},
                {'name': 'Property Tax', 'amount': total_amount * 0.1},
                {'name': 'Home Maintenance', 'amount': total_amount * 0.1}
            ],
            'Utilities': [
                {'name': 'Electricity', 'amount': total_amount * 0.4},
                {'name': 'Water', 'amount': total_amount * 0.2},
                {'name': 'Gas', 'amount': total_amount * 0.2},
                {'name': 'Internet', 'amount': total_amount * 0.2}
            ],
            'Transportation': [
                {'name': 'Fuel/Public Transport', 'amount': total_amount * 0.6},
                {'name': 'Vehicle Maintenance', 'amount': total_amount * 0.3},
                {'name': 'Parking', 'amount': total_amount * 0.1}
            ],
            'Groceries': [
                {'name': 'Food & Beverages', 'amount': total_amount * 0.8},
                {'name': 'Household Items', 'amount': total_amount * 0.2}
            ],
            'Healthcare': [
                {'name': 'Medical Checkups', 'amount': total_amount * 0.4},
                {'name': 'Medications', 'amount': total_amount * 0.4},
                {'name': 'Emergency Fund', 'amount': total_amount * 0.2}
            ],
            'Entertainment': [
                {'name': 'Movies/Shows', 'amount': total_amount * 0.4},
                {'name': 'Sports/Hobbies', 'amount': total_amount * 0.4},
                {'name': 'Social Events', 'amount': total_amount * 0.2}
            ]
        }
        
        # Default items for categories not specified
        default_items = [{'name': f'{category} Expenses', 'amount': total_amount}]
        
        items = category_items.get(category, default_items)
        
        # Round amounts to 2 decimal places
        for item in items:
            item['amount'] = round(item['amount'], 2)
        
        return items
    
    def _fallback_category_amount(self, income: float, category: str) -> float:
        """
        Fallback method for estimating category amounts
        """
        category_percentages = {
            'Housing': 0.30,
            'Utilities': 0.10,
            'Groceries': 0.15,
            'Transportation': 0.10,
            'Healthcare': 0.05,
            'Insurance': 0.03,
            'Education': 0.02,
            'Savings': 0.10,
            'Debt Payments': 0.05,
            'Personal Care': 0.03,
            'Entertainment': 0.05,
            'Dining Out': 0.08,
            'Clothing': 0.03,
            'Gifts & Donations': 0.02,
            'Travel': 0.03,
            'Childcare': 0.15,
            'Pets': 0.02,
            'Other': 0.05
        }
        
        percentage = category_percentages.get(category, 0.05)
        return round(income * percentage, 2)
    
    def _adjust_budget_to_income(self, budget: Dict) -> Dict:
        """
        Adjust budget to ensure it doesn't exceed income
        """
        total_budget = budget['total_budget']
        monthly_income = budget['monthly_income']
        
        if total_budget > monthly_income * 0.95:  # Leave 5% buffer
            # Scale down all categories proportionally
            scale_factor = (monthly_income * 0.95) / total_budget
            
            for category in budget['categories']:
                old_amount = budget['categories'][category]['amount']
                new_amount = old_amount * scale_factor
                budget['categories'][category]['amount'] = round(new_amount, 2)
                
                # Adjust items proportionally
                for item in budget['categories'][category]['items']:
                    item['amount'] = round(item['amount'] * scale_factor, 2)
            
            budget['total_budget'] = round(total_budget * scale_factor, 2)
        
        return budget
    
    def save_budget_to_database(self, budget: Dict) -> bool:
        """
        Save generated budget to database
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
                    'AI Generated Budget',
                    'USD',  # Default currency
                    budget['total_budget']
                ))
                
                # Create category records
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
                            'AI Generated Item'
                        ))
                
                conn.commit()
                logger.info(f"Budget saved successfully for user {budget['user_id']}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving budget to database: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def _save_models(self):
        """
        Save trained models to disk
        """
        try:
            joblib.dump(self.models, 'models/budget_models.pkl')
            joblib.dump(self.scalers, 'models/budget_scalers.pkl')
            joblib.dump(self.label_encoders, 'models/budget_encoders.pkl')
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def _load_models(self):
        """
        Load trained models from disk
        """
        try:
            logger.info("Loading trained ML models from disk...")
            
            self.models = joblib.load('models/budget_models.pkl')
            self.scalers = joblib.load('models/budget_scalers.pkl')
            self.label_encoders = joblib.load('models/budget_encoders.pkl')
            
            self.model_trained = True
            
            logger.info(f"✅ Successfully loaded {len(self.models)} trained models:")
            for category in self.models.keys():
                model = self.models[category]
                logger.info(f"   - {category}: {type(model).__name__} with {model.n_estimators} estimators")
                
        except FileNotFoundError as e:
            logger.error(f"❌ Model files not found: {e}")
            logger.error("Please train the models first using the training script!")
            self.model_trained = False
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            self.model_trained = False

# Create global instance
budget_generator = BudgetMLGenerator()
