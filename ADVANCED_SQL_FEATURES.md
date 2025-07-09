# Advanced SQL Features Documentation

This document describes the advanced SQL features implemented in the FinGuard FinTech application, including stored procedures, functions, triggers, and complex queries.

## Overview

The advanced SQL features enhance the backend data operations with:
- **Stored Procedures**: Complex business logic executed on the database server
- **Functions**: Reusable calculations and data processing
- **Triggers**: Automatic actions on data changes for auditing and validation
- **Views**: Pre-defined complex queries for reporting and analytics
- **Complex Queries**: Advanced SQL with CTEs, window functions, and subqueries

## Installation

1. **Apply the Advanced SQL Features**:
   ```bash
   python apply_advanced_sql.py
   ```

2. **Test the Installation**:
   ```bash
   python test_advanced_sql.py
   ```

## Stored Procedures

### ProcessMoneyTransfer
Enhanced money transfer with comprehensive validation and fraud checking.

**Parameters**:
- `p_sender_id`: Sender user ID
- `p_receiver_id`: Receiver user ID  
- `p_amount`: Transfer amount
- `p_payment_method`: Payment method
- `p_note`: Transaction note
- `p_tx_type`: Transaction type
- `p_location`: Transaction location
- `p_success` (OUT): Success flag
- `p_message` (OUT): Result message
- `p_transaction_id` (OUT): Generated transaction ID

**Features**:
- Input validation (positive amounts, different sender/receiver)
- Balance verification
- Fraud list checking
- Atomic transaction processing
- Detailed error messages

**Usage in Python**:
```python
from app.utils.advanced_sql_utils import AdvancedSQLUtils

success, message, tx_id = AdvancedSQLUtils.process_money_transfer(
    sender_id, receiver_id, amount, payment_method, note, tx_type, location
)
```

### GetUserTransactionHistory
Retrieve user transaction history with analytics.

**Parameters**:
- `p_user_id`: User ID
- `p_limit`: Number of transactions to return
- `p_offset`: Offset for pagination

**Returns**: Transaction records with direction, counterparty info, and running balance.

### CalculateUserStatistics
Calculate comprehensive user statistics.

**Parameters**:
- `p_user_id`: User ID
- `p_total_sent` (OUT): Total amount sent
- `p_total_received` (OUT): Total amount received
- `p_transaction_count` (OUT): Number of transactions
- `p_avg_transaction` (OUT): Average transaction amount
- `p_last_transaction_date` (OUT): Last transaction date

### BulkBalanceUpdate
Admin function for bulk balance updates with logging.

**Parameters**:
- `p_admin_id`: Admin user ID
- `p_user_ids`: User IDs (comma-separated)
- `p_amounts`: Amounts (comma-separated)
- `p_reason`: Update reason
- `p_success` (OUT): Success flag
- `p_message` (OUT): Result message

## Functions

### CalculateAccountAge(user_id)
Returns the age of a user account in days.

**Usage**:
```sql
SELECT CalculateAccountAge('user-id-here') as age_days;
```

### CalculateTransactionVelocity(user_id, days)
Returns the average transactions per day for a user over the specified period.

**Usage**:
```sql
SELECT CalculateTransactionVelocity('user-id-here', 30) as monthly_velocity;
```

### GetUserRiskScore(user_id)
Calculates a risk score (0-100) based on fraud reports, transaction patterns, and account age.

**Factors**:
- Fraud reports: +30 points each
- High-amount transactions (>1000): +10 points each
- Account age: Reduces score for older accounts

**Usage**:
```sql
SELECT GetUserRiskScore('user-id-here') as risk_score;
```

## Triggers

### tr_users_admin_log
Automatically logs administrative changes to user accounts.

**Triggered on**: UPDATE of users table
**Logs**: Balance changes and role changes

### tr_transactions_validate
Validates transaction data before insertion.

**Validations**:
- Amount must be positive
- Sender and receiver must be different
- Auto-sets timestamp if not provided

### tr_transactions_blockchain
Automatically creates blockchain records for transactions.

**Actions**:
- Creates blockchain_transactions record
- Generates hash for blockchain integrity
- Links to blockchain table

### tr_update_user_activity
Logs user activity when transactions occur.

**Triggered on**: INSERT into transactions table
**Action**: Creates admin log entry for transaction activity

## Views

### v_user_transaction_summary
Comprehensive user transaction summary with risk scores.

**Columns**:
- User information (id, name, balance)
- Transaction counts (sent/received)
- Transaction totals (sent/received amounts)
- Last transaction date
- Risk score

**Usage**:
```sql
SELECT * FROM v_user_transaction_summary 
ORDER BY total_sent + total_received DESC;
```

### v_daily_transaction_analytics
Daily transaction analytics for the last 30 days.

**Columns**:
- Date, transaction count, total volume
- Average/min/max transaction amounts
- Unique senders/receivers
- Transaction type breakdowns

### v_high_risk_users
Users with high risk scores and their metrics.

**Columns**:
- User information
- Risk score, fraud reports
- Transaction velocity, account age

**Usage**:
```sql
SELECT * FROM v_high_risk_users WHERE risk_score > 50;
```

## Python Integration

### AdvancedSQLUtils Class
Provides Python interface to stored procedures and functions.

```python
from app.utils.advanced_sql_utils import AdvancedSQLUtils

# Process money transfer
success, message, tx_id = AdvancedSQLUtils.process_money_transfer(...)

# Get user statistics
stats = AdvancedSQLUtils.calculate_user_statistics(user_id)

# Get risk score
risk = AdvancedSQLUtils.get_user_risk_score(user_id)

# Calculate account age
age = AdvancedSQLUtils.calculate_account_age(user_id)
```

### AdvancedReportingUtils Class
Provides access to complex reporting queries and views.

```python
from app.utils.advanced_sql_utils import AdvancedReportingUtils

# Get user transaction summary
summary = AdvancedReportingUtils.get_user_transaction_summary()

# Get daily analytics
analytics = AdvancedReportingUtils.get_daily_analytics()

# Get high risk users
risky_users = AdvancedReportingUtils.get_high_risk_users()

# Get fraud detection insights
insights = AdvancedReportingUtils.get_fraud_detection_insights()
```

### Enhanced Admin Utils
Admin utilities now support advanced SQL features.

```python
from app.utils.admin_utils import (
    admin_bulk_balance_update,
    get_comprehensive_user_stats,
    get_admin_dashboard_data,
    get_fraud_monitoring_report
)

# Bulk balance update with stored procedure
success, message = admin_bulk_balance_update(admin_id, user_id, amount, reason)

# Get comprehensive user stats
stats = get_comprehensive_user_stats(user_id)

# Get admin dashboard data
dashboard = get_admin_dashboard_data()
```

## Complex Queries

### Monthly Transaction Report with Running Totals
```sql
WITH monthly_data AS (
    SELECT 
        YEAR(timestamp) as year,
        MONTH(timestamp) as month,
        COUNT(*) as transaction_count,
        SUM(amount) as total_volume,
        AVG(amount) as avg_amount
    FROM transactions
    GROUP BY YEAR(timestamp), MONTH(timestamp)
),
running_totals AS (
    SELECT 
        year, month,
        transaction_count, total_volume, avg_amount,
        SUM(transaction_count) OVER (ORDER BY year, month) as cumulative_transactions,
        SUM(total_volume) OVER (ORDER BY year, month) as cumulative_volume
    FROM monthly_data
)
SELECT * FROM running_totals
ORDER BY year DESC, month DESC;
```

### Transaction Pattern Analysis
Advanced analysis with multiple subqueries and window functions for detecting patterns in user behavior.

### Fraud Detection Queries
Complex queries that identify:
- High-velocity users (unusual transaction frequency)
- Round amount transactions (potential money laundering)
- Off-hours transactions (unusual timing)
- Rapid sequence transactions (potential automation)

## Performance Considerations

1. **Indexes**: Ensure proper indexing on frequently queried columns
2. **Query Optimization**: Stored procedures are pre-compiled for better performance
3. **Connection Pooling**: Use with connection pooling for production
4. **Monitoring**: Monitor trigger performance as they execute on every data change

## Security Features

1. **SQL Injection Prevention**: Parameterized queries throughout
2. **Access Control**: Functions and procedures can be granted specific permissions
3. **Audit Logging**: Automatic logging of sensitive operations
4. **Data Validation**: Input validation in stored procedures and triggers

## Maintenance

1. **Backup**: Include stored procedures, functions, and views in database backups
2. **Version Control**: Track changes to SQL objects
3. **Testing**: Use the test script to verify functionality after changes
4. **Documentation**: Keep this documentation updated with changes

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure database user has CREATE, ALTER, and EXECUTE privileges
2. **Syntax Errors**: Check MySQL version compatibility (requires 5.7+)
3. **Missing Dependencies**: Ensure all required tables exist before applying features
4. **Performance Issues**: Monitor trigger execution times and optimize if needed

### Debug Commands

```sql
-- Check stored procedures
SHOW PROCEDURE STATUS WHERE Db = 'fin_guard';

-- Check functions  
SHOW FUNCTION STATUS WHERE Db = 'fin_guard';

-- Check triggers
SHOW TRIGGERS;

-- Check views
SHOW FULL TABLES WHERE Table_type = 'VIEW';
```

## Future Enhancements

1. **Partitioning**: Consider table partitioning for large transaction tables
2. **Caching**: Implement query result caching for reporting views
3. **Advanced Analytics**: Add more sophisticated ML-based fraud detection
4. **Real-time Processing**: Consider event-driven architecture for real-time fraud detection
5. **API Integration**: Expose advanced features through REST APIs