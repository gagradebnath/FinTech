# Advanced Analytics Route - Demonstrates the new SQL features
from flask import Blueprint, render_template, jsonify, request
from app.utils.advanced_sql_utils import AdvancedSQLUtils, AdvancedReportingUtils
from app.utils.admin_utils import get_admin_dashboard_data, get_fraud_monitoring_report

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/dashboard')
def analytics_dashboard():
    """Advanced analytics dashboard using new SQL features"""
    try:
        dashboard_data = get_admin_dashboard_data()
        return render_template('analytics/dashboard.html', data=dashboard_data)
    except Exception as e:
        return jsonify({'error': f'Failed to load dashboard: {str(e)}'}), 500

@analytics_bp.route('/api/user-stats/<user_id>')
def user_statistics_api(user_id):
    """API endpoint for comprehensive user statistics"""
    try:
        stats = AdvancedSQLUtils.calculate_user_statistics(user_id)
        risk_score = AdvancedSQLUtils.get_user_risk_score(user_id)
        account_age = AdvancedSQLUtils.calculate_account_age(user_id)
        velocity = AdvancedSQLUtils.calculate_transaction_velocity(user_id, 30)
        
        return jsonify({
            'success': True,
            'data': {
                'statistics': stats,
                'risk_score': risk_score,
                'account_age_days': account_age,
                'monthly_velocity': velocity
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/transaction-history/<user_id>')
def transaction_history_api(user_id):
    """API endpoint for enhanced transaction history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        history = AdvancedSQLUtils.get_user_transaction_history(user_id, limit, offset)
        
        return jsonify({
            'success': True,
            'data': history,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'returned': len(history)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/daily-analytics')
def daily_analytics_api():
    """API endpoint for daily transaction analytics"""
    try:
        analytics = AdvancedReportingUtils.get_daily_analytics()
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/high-risk-users')
def high_risk_users_api():
    """API endpoint for high risk users"""
    try:
        users = AdvancedReportingUtils.get_high_risk_users()
        return jsonify({'success': True, 'data': users})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/fraud-insights')
def fraud_insights_api():
    """API endpoint for fraud detection insights"""
    try:
        insights = AdvancedReportingUtils.get_fraud_detection_insights()
        return jsonify({'success': True, 'data': insights})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/monthly-report')
def monthly_report_api():
    """API endpoint for monthly transaction report with running totals"""
    try:
        report = AdvancedReportingUtils.get_monthly_transaction_report()
        return jsonify({'success': True, 'data': report})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/api/pattern-analysis/<user_id>')
def pattern_analysis_api(user_id):
    """API endpoint for transaction pattern analysis"""
    try:
        analysis = AdvancedReportingUtils.get_transaction_pattern_analysis(user_id)
        return jsonify({'success': True, 'data': analysis})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@analytics_bp.route('/test-features')
def test_features():
    """Test page to demonstrate advanced SQL features"""
    try:
        # Test various features and display results
        test_results = {
            'user_summary': AdvancedReportingUtils.get_user_transaction_summary()[:5],
            'daily_analytics': AdvancedReportingUtils.get_daily_analytics()[:3],
            'high_risk_users': AdvancedReportingUtils.get_high_risk_users()[:3],
            'fraud_insights': AdvancedReportingUtils.get_fraud_detection_insights()
        }
        
        return render_template('analytics/test_features.html', results=test_results)
    except Exception as e:
        return f"<h1>Error Testing Features</h1><p>{str(e)}</p><p>Make sure to run: <code>python apply_advanced_sql.py</code></p>"

# Register the blueprint
def register_analytics_blueprint(app):
    """Register the analytics blueprint with the Flask app"""
    app.register_blueprint(analytics_bp)