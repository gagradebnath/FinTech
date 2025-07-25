"""
ML Budget Route - Flask routes for machine learning budget generation
"""

from flask import Blueprint, request, jsonify, session, render_template
from app.utils.ml_budget_generator import budget_generator
from app.utils.auth import login_required
import logging

logger = logging.getLogger(__name__)

ml_budget_bp = Blueprint('ml_budget', __name__)

@ml_budget_bp.route('/train-budget-models', methods=['POST'])
@login_required
def train_budget_models():
    """
    Train ML models for budget generation
    This should be called by admin users to train/retrain the models
    """
    try:
        # Check if user has admin privileges (you may want to implement this check)
        user_id = session.get('user_id')
        
        # Train the models
        success = budget_generator.train_models()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Budget ML models trained successfully',
                'models_trained': len(budget_generator.models)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to train budget models. Check if there is sufficient data.'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in train_budget_models: {e}")
        return jsonify({
            'success': False,
            'message': f'Error training models: {str(e)}'
        }), 500

@ml_budget_bp.route('/generate-ai-budget', methods=['POST'])
@login_required
def generate_ai_budget():
    """
    Generate AI-powered budget for the current user
    """
    try:
        user_id = session.get('user_id')
        
        # Generate budget using ML
        budget = budget_generator.generate_budget_for_user(user_id)
        
        if not budget:
            return jsonify({
                'success': False,
                'message': 'Could not generate budget. Please ensure you have filled out your expense habits.'
            }), 400
        
        # Save to database
        save_success = budget_generator.save_budget_to_database(budget)
        
        if save_success:
            return jsonify({
                'success': True,
                'message': 'AI budget generated and saved successfully',
                'budget': budget
            })
        else:
            return jsonify({
                'success': True,
                'message': 'Budget generated but could not be saved to database',
                'budget': budget
            })
            
    except Exception as e:
        logger.error(f"Error in generate_ai_budget: {e}")
        return jsonify({
            'success': False,
            'message': f'Error generating budget: {str(e)}'
        }), 500

@ml_budget_bp.route('/preview-ai-budget', methods=['GET'])
@login_required
def preview_ai_budget():
    """
    Preview AI-generated budget without saving to database
    """
    try:
        user_id = session.get('user_id')
        
        # Generate budget using ML
        budget = budget_generator.generate_budget_for_user(user_id)
        
        if not budget:
            return jsonify({
                'success': False,
                'message': 'Could not generate budget preview. Please ensure you have filled out your expense habits.'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Budget preview generated successfully',
            'budget': budget
        })
            
    except Exception as e:
        logger.error(f"Error in preview_ai_budget: {e}")
        return jsonify({
            'success': False,
            'message': f'Error generating budget preview: {str(e)}'
        }), 500

@ml_budget_bp.route('/ai-budget-dashboard')
@login_required
def ai_budget_dashboard():
    """
    Render AI budget dashboard page
    """
    try:
        user_id = session.get('user_id')
        return render_template('ai_budget_dashboard.html', user_id=user_id)
    except Exception as e:
        logger.error(f"Error rendering AI budget dashboard: {e}")
        return "Error loading AI budget dashboard", 500

@ml_budget_bp.route('/retrain-models', methods=['POST'])
@login_required
def retrain_models():
    """
    Retrain models with new data (admin function)
    """
    try:
        # This should ideally check for admin privileges
        user_id = session.get('user_id')
        
        # Force retrain models
        budget_generator.model_trained = False
        success = budget_generator.train_models()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Models retrained successfully',
                'models_count': len(budget_generator.models)
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to retrain models'
            }), 400
            
    except Exception as e:
        logger.error(f"Error in retrain_models: {e}")
        return jsonify({
            'success': False,
            'message': f'Error retraining models: {str(e)}'
        }), 500

@ml_budget_bp.route('/model-status', methods=['GET'])
@login_required
def model_status():
    """
    Get detailed status of ML models
    """
    try:
        # Force load models to check if they exist
        if not budget_generator.model_trained:
            budget_generator._load_models()
        
        model_details = {}
        if budget_generator.models:
            for category, model in budget_generator.models.items():
                model_details[category] = {
                    'type': type(model).__name__,
                    'n_estimators': getattr(model, 'n_estimators', 'N/A'),
                    'max_depth': getattr(model, 'max_depth', 'N/A')
                }
        
        return jsonify({
            'success': True,
            'model_trained': budget_generator.model_trained,
            'models_count': len(budget_generator.models),
            'available_categories': list(budget_generator.models.keys()) if budget_generator.models else [],
            'model_details': model_details,
            'scalers_count': len(budget_generator.scalers),
            'encoders_count': len(budget_generator.label_encoders)
        })
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        return jsonify({
            'success': False,
            'message': f'Error getting model status: {str(e)}'
        }), 500

@ml_budget_bp.route('/budget-recommendations/<user_id>', methods=['GET'])
@login_required
def get_budget_recommendations(user_id):
    """
    Get budget recommendations for a specific user (admin function)
    """
    try:
        # Generate budget recommendations
        budget = budget_generator.generate_budget_for_user(user_id)
        
        if not budget:
            return jsonify({
                'success': False,
                'message': 'Could not generate recommendations for this user'
            }), 400
        
        return jsonify({
            'success': True,
            'recommendations': budget
        })
            
    except Exception as e:
        logger.error(f"Error in get_budget_recommendations: {e}")
        return jsonify({
            'success': False,
            'message': f'Error generating recommendations: {str(e)}'
        }), 500
