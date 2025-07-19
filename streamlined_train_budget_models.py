"""
Streamlined Budget ML Training Script for FinGuard
Generates synthetic data on-the-fly and trains ML models without saving generated data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
import logging
from typing import Dict, List, Tuple
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Expense categories
EXPENSE_CATEGORIES = [
    'Housing', 'Utilities', 'Groceries', 'Transportation', 'Healthcare',
    'Insurance', 'Education', 'Savings', 'Debt Payments', 'Personal Care',
    'Entertainment', 'Dining Out', 'Clothing', 'Gifts & Donations',
    'Travel', 'Childcare', 'Pets', 'Other'
]

class StreamlinedBudgetMLTrainer:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        
    def generate_synthetic_data(self, num_records: int = 30000) -> pd.DataFrame:
        """
        Generate synthetic expense habit data for training
        """
        logger.info(f"Generating {num_records} synthetic records...")
        
        # Define realistic ranges and options
        genders = ['Male', 'Female', 'Other']
        marital_statuses = ['Single', 'Married', 'Divorced', 'Widowed']
        living_situations = ['Rent', 'Own', 'Family', 'Shared']
        transport_modes = ['Car', 'Public Transport', 'Bike', 'Walk']
        eating_frequencies = ['Daily', 'Weekly', 'Monthly', 'Rarely']
        savings_habits = ['High', 'Medium', 'Low', 'None']
        countries = ['Bangladesh', 'India', 'Pakistan', 'USA', 'UK']
        divisions = ['Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi', 'Khulna']
        
        # Income ranges with realistic distributions
        income_ranges = [
            ('below 20000', 15000),
            ('20000-40000', 30000),
            ('40000-60000', 50000),
            ('60000-80000', 70000),
            ('80000-100000', 90000),
            ('above 100000', 120000)
        ]
        
        data = []
        
        for i in range(num_records):
            # Basic demographics
            age = np.random.normal(35, 12)  # Mean age 35, std 12
            age = max(18, min(80, int(age)))  # Constrain to realistic range
            
            gender = random.choice(genders)
            marital_status = random.choice(marital_statuses)
            
            # Dependents based on age and marital status
            if marital_status == 'Single' and age < 30:
                dependents = np.random.choice([0, 1], p=[0.8, 0.2])
            elif marital_status == 'Married':
                dependents = np.random.choice([0, 1, 2, 3, 4], p=[0.1, 0.3, 0.4, 0.15, 0.05])
            else:
                dependents = np.random.choice([0, 1, 2], p=[0.5, 0.3, 0.2])
            
            # Income based on age and demographics
            if age < 25:
                income_idx = np.random.choice(len(income_ranges[:3]), p=[0.5, 0.4, 0.1])
                income_choice = income_ranges[:3][income_idx]
            elif age < 35:
                income_idx = np.random.choice(len(income_ranges[1:5]), p=[0.3, 0.4, 0.2, 0.1])
                income_choice = income_ranges[1:5][income_idx]
            elif age < 50:
                income_idx = np.random.choice(len(income_ranges[2:]), p=[0.2, 0.3, 0.3, 0.2])
                income_choice = income_ranges[2:][income_idx]
            else:
                income_idx = np.random.choice(len(income_ranges[3:]), p=[0.3, 0.4, 0.3])
                income_choice = income_ranges[3:][income_idx]
            
            monthly_income_str, monthly_income_numeric = income_choice
            
            # Living situation affects rent
            living_situation = random.choice(living_situations)
            if living_situation == 'Family':
                rent = 0
            elif living_situation == 'Shared':
                rent = monthly_income_numeric * np.random.uniform(0.15, 0.25)
            elif living_situation == 'Own':
                rent = monthly_income_numeric * np.random.uniform(0.20, 0.35)
            else:  # Rent
                rent = monthly_income_numeric * np.random.uniform(0.25, 0.40)
            
            # Other expenses based on income and lifestyle
            transport_mode = random.choice(transport_modes)
            if transport_mode == 'Car':
                transport_cost = monthly_income_numeric * np.random.uniform(0.08, 0.15)
            elif transport_mode == 'Public Transport':
                transport_cost = monthly_income_numeric * np.random.uniform(0.03, 0.08)
            else:
                transport_cost = monthly_income_numeric * np.random.uniform(0.01, 0.03)
            
            # Grocery costs based on family size
            base_grocery = monthly_income_numeric * 0.12
            grocery_cost = base_grocery * (1 + dependents * 0.3)
            
            # Utilities based on living situation
            if living_situation == 'Family':
                utilities_cost = monthly_income_numeric * np.random.uniform(0.02, 0.05)
            else:
                utilities_cost = monthly_income_numeric * np.random.uniform(0.05, 0.12)
            
            # Other costs
            mobile_internet_cost = monthly_income_numeric * np.random.uniform(0.02, 0.05)
            
            # Loan payment (some people have loans)
            has_loan = np.random.choice([True, False], p=[0.3, 0.7])
            if has_loan:
                loan_payment = monthly_income_numeric * np.random.uniform(0.05, 0.20)
            else:
                loan_payment = 0
            
            # Other categorical data
            eating_out_frequency = random.choice(eating_frequencies)
            savings = random.choice(savings_habits)
            country = random.choice(countries)
            division = random.choice(divisions)
            district = f"District_{random.randint(1, 10)}"
            earning_member = np.random.choice([True, False], p=[0.8, 0.2])
            
            # Create record
            record = {
                'user_id': f"user_{i+1}",
                'age': age,
                'gender': gender,
                'marital_status': marital_status,
                'dependents': dependents,
                'living_situation': living_situation,
                'transport_mode': transport_mode,
                'eating_out_frequency': eating_out_frequency,
                'savings': savings,
                'country': country,
                'division': division,
                'district': district,
                'earning_member': earning_member,
                'monthly_income': monthly_income_str,
                'monthly_income_numeric': monthly_income_numeric,
                'rent': max(0, rent),
                'transport_cost': max(0, transport_cost),
                'grocery_cost': max(0, grocery_cost),
                'utilities_cost': max(0, utilities_cost),
                'mobile_internet_cost': max(0, mobile_internet_cost),
                'loan_payment': max(0, loan_payment)
            }
            
            data.append(record)
        
        df = pd.DataFrame(data)
        logger.info(f"Generated synthetic dataset with {len(df)} records")
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the data for ML training
        """
        logger.info("Preprocessing data...")
        
        # Create derived features
        df['total_fixed_expenses'] = (
            df['rent'] + df['utilities_cost'] + 
            df['mobile_internet_cost'] + df['loan_payment']
        )
        
        df['total_variable_expenses'] = (
            df['transport_cost'] + df['grocery_cost']
        )
        
        df['income_expense_ratio'] = df['monthly_income_numeric'] / (
            df['total_fixed_expenses'] + df['total_variable_expenses'] + 1
        )
        
        df['expense_per_dependent'] = df['total_fixed_expenses'] / (df['dependents'] + 1)
        df['age_income_ratio'] = df['age'] / (df['monthly_income_numeric'] / 1000)
        
        # Encode categorical variables
        categorical_columns = [
            'gender', 'marital_status', 'living_situation', 
            'transport_mode', 'eating_out_frequency', 'savings',
            'country', 'division', 'district'
        ]
        
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
        
        return df
    
    def create_target_variables(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Create target variables for each expense category
        """
        targets = {}
        
        # Direct mappings from existing data
        direct_mappings = {
            'Housing': 'rent',
            'Utilities': 'utilities_cost',
            'Groceries': 'grocery_cost',
            'Transportation': 'transport_cost',
            'Debt Payments': 'loan_payment',
            'Personal Care': 'mobile_internet_cost'
        }
        
        # Add some realistic variance to direct mappings
        for category, column in direct_mappings.items():
            base_values = df[column]
            # Add 10% random variance
            noise = np.random.normal(0, base_values.std() * 0.1, len(df))
            targets[category] = np.maximum(0, base_values + noise)
        
        # Percentage-based estimates for other categories
        income = df['monthly_income_numeric']
        
        category_percentages = {
            'Healthcare': (0.03, 0.08),      # 3-8% of income
            'Insurance': (0.02, 0.05),       # 2-5% of income
            'Education': (0.01, 0.06),       # 1-6% of income (higher for families with kids)
            'Savings': (0.05, 0.20),         # 5-20% of income
            'Entertainment': (0.03, 0.10),   # 3-10% of income
            'Dining Out': (0.05, 0.15),      # 5-15% of income
            'Clothing': (0.02, 0.06),        # 2-6% of income
            'Gifts & Donations': (0.01, 0.05), # 1-5% of income
            'Travel': (0.02, 0.08),          # 2-8% of income
            'Childcare': (0.00, 0.25),       # 0-25% depending on dependents
            'Pets': (0.01, 0.04),            # 1-4% of income
            'Other': (0.02, 0.08)            # 2-8% of income
        }
        
        for category, (min_pct, max_pct) in category_percentages.items():
            if category == 'Education':
                # Higher for families with dependents
                pct = np.where(df['dependents'] > 0, 
                              np.random.uniform(0.03, 0.06, len(df)),
                              np.random.uniform(0.01, 0.03, len(df)))
            elif category == 'Childcare':
                # Only for families with dependents
                pct = np.where(df['dependents'] > 0,
                              np.random.uniform(0.10, 0.25, len(df)),
                              np.random.uniform(0.00, 0.02, len(df)))
            elif category == 'Savings':
                # Based on savings habit
                savings_mapping = {'High': (0.15, 0.25), 'Medium': (0.08, 0.15), 
                                 'Low': (0.03, 0.08), 'None': (0.00, 0.02)}
                pct = np.zeros(len(df))
                for habit, (low, high) in savings_mapping.items():
                    mask = df['savings'] == habit
                    pct[mask] = np.random.uniform(low, high, mask.sum())
            else:
                pct = np.random.uniform(min_pct, max_pct, len(df))
            
            targets[category] = income * pct
        
        return targets
    
    def train_models(self, df: pd.DataFrame, targets: Dict[str, pd.Series]) -> bool:
        """
        Train ML models for each expense category
        """
        logger.info("Training ML models...")
        
        # Feature columns
        feature_columns = [
            'monthly_income_numeric', 'age', 'dependents', 'earning_member',
            'total_fixed_expenses', 'total_variable_expenses', 'income_expense_ratio',
            'expense_per_dependent', 'age_income_ratio'
        ]
        
        # Add encoded categorical features
        encoded_columns = [col for col in df.columns if col.endswith('_encoded')]
        feature_columns.extend(encoded_columns)
        
        # Convert boolean to numeric
        df['earning_member'] = df['earning_member'].astype(int)
        
        X = df[feature_columns]
        
        # Train models for each category
        for category in EXPENSE_CATEGORIES:
            if category not in targets:
                logger.warning(f"No target data for category: {category}")
                continue
                
            try:
                y = targets[category]
                
                # Skip if no variance
                if y.std() < 0.01:
                    logger.warning(f"No variance in target for {category}, skipping...")
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
                    min_samples_split=5,
                    min_samples_leaf=2
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
        
        return len(self.models) > 0
    
    def save_models(self, model_dir: str = "models"):
        """
        Save trained models to disk
        """
        os.makedirs(model_dir, exist_ok=True)
        
        try:
            joblib.dump(self.models, f'{model_dir}/budget_models.pkl')
            joblib.dump(self.scalers, f'{model_dir}/budget_scalers.pkl')
            joblib.dump(self.label_encoders, f'{model_dir}/budget_encoders.pkl')
            logger.info(f"Models saved successfully to {model_dir}")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def test_prediction(self, df: pd.DataFrame) -> Dict:
        """
        Test prediction with a sample user
        """
        logger.info("Testing prediction with sample user...")
        
        # Take first user as sample
        sample_user = df.iloc[0].to_dict()
        
        # Prepare features
        feature_columns = [
            'monthly_income_numeric', 'age', 'dependents', 'earning_member',
            'total_fixed_expenses', 'total_variable_expenses', 'income_expense_ratio',
            'expense_per_dependent', 'age_income_ratio'
        ]
        
        # Add encoded categorical features
        encoded_columns = [col for col in df.columns if col.endswith('_encoded')]
        feature_columns.extend(encoded_columns)
        
        user_features = [sample_user[col] for col in feature_columns]
        user_features = np.array(user_features).reshape(1, -1)
        
        # Generate predictions
        budget = {
            'user_id': sample_user['user_id'],
            'monthly_income': sample_user['monthly_income_numeric'],
            'categories': {},
            'total_budget': 0
        }
        
        for category in EXPENSE_CATEGORIES:
            if category in self.models:
                try:
                    model = self.models[category]
                    scaler = self.scalers[category]
                    
                    user_features_scaled = scaler.transform(user_features)
                    predicted_amount = model.predict(user_features_scaled)[0]
                    predicted_amount = max(0, predicted_amount)
                    
                    budget['categories'][category] = round(predicted_amount, 2)
                    budget['total_budget'] += predicted_amount
                    
                except Exception as e:
                    logger.error(f"Error predicting for {category}: {e}")
        
        budget['total_budget'] = round(budget['total_budget'], 2)
        
        # Show sample prediction
        logger.info(f"Sample prediction for user {sample_user['user_id']}:")
        logger.info(f"  Monthly Income: ${budget['monthly_income']:.2f}")
        logger.info(f"  Total Budget: ${budget['total_budget']:.2f}")
        logger.info("  Top categories:")
        
        # Sort and show top 5 categories
        sorted_categories = sorted(budget['categories'].items(), 
                                 key=lambda x: x[1], reverse=True)[:5]
        for cat, amount in sorted_categories:
            logger.info(f"    {cat}: ${amount:.2f}")
        
        return budget

def main():
    """
    Main training function
    """
    print("Streamlined Budget ML Training Script")
    print("=" * 50)
    
    trainer = StreamlinedBudgetMLTrainer()
    
    try:
        # Step 1: Generate synthetic data
        print("\n1. Generating synthetic training data...")
        df = trainer.generate_synthetic_data(num_records=30000)
        print(f"✓ Generated {len(df)} training records")
        
        # Step 2: Preprocess data
        print("\n2. Preprocessing data...")
        df = trainer.preprocess_data(df)
        print("✓ Data preprocessing completed")
        
        # Step 3: Create target variables
        print("\n3. Creating target variables...")
        targets = trainer.create_target_variables(df)
        print(f"✓ Created targets for {len(targets)} categories")
        
        # Step 4: Train models
        print("\n4. Training ML models...")
        success = trainer.train_models(df, targets)
        
        if success:
            print(f"✓ Successfully trained {len(trainer.models)} models")
            
            # Step 5: Save models
            print("\n5. Saving models...")
            trainer.save_models()
            print("✓ Models saved successfully")
            
            # Step 6: Test prediction
            print("\n6. Testing prediction...")
            sample_budget = trainer.test_prediction(df)
            print("✓ Prediction test completed")
            
            print(f"\n🎉 Training completed successfully!")
            print(f"   - Trained models: {len(trainer.models)}")
            print(f"   - Training data: {len(df)} records")
            print(f"   - Categories covered: {', '.join(trainer.models.keys())}")
            
        else:
            print("✗ Model training failed")
            return False
            
    except Exception as e:
        logger.error(f"Training failed: {e}")
        print(f"✗ Training failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
