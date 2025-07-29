from flask import Blueprint, request, jsonify, render_template, session
import requests
import json
from datetime import datetime
from .user import get_current_user
from app.utils.jwt_auth import get_current_user_from_jwt

chat_bp = Blueprint('chat', __name__)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:3b"

@chat_bp.route('/chat', methods=['GET'])
def chat_page():
    """Render the chat interface"""
    return render_template('chat.html')

@chat_bp.route('/api/chat', methods=['POST'])
def chat_api():
    """Handle chat messages and communicate with Ollama"""
    try:
        # Get current user
        user = get_current_user_from_jwt()
        if not user:
            user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message']
        
        # Prepare context for the financial assistant
        system_prompt = """You are FinGuard Assistant, a helpful AI chatbot for a financial management application called FinGuard. 
        You help users with:
        - Budget planning and management
        - Expense tracking advice
        - Financial planning tips
        - Understanding FinGuard features
        - General financial advice
        
        Keep your responses concise, helpful, and focused on personal finance. 
        If users ask about features, explain how FinGuard can help them manage their money better.
        Always be encouraging and supportive about their financial journey."""
        
        # Prepare the request to Ollama
        ollama_request = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
        
        # Send request to Ollama
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=ollama_request,
                timeout=30
            )
            
            if response.status_code == 200:
                ollama_response = response.json()
                bot_message = ollama_response.get('message', {}).get('content', 'Sorry, I could not generate a response.')
                
                # Log the conversation (optional)
                chat_log = {
                    'user_id': user['id'],
                    'user_message': user_message,
                    'bot_response': bot_message,
                    'timestamp': datetime.now().isoformat()
                }
                
                return jsonify({
                    'success': True,
                    'response': bot_message,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to get response from AI model',
                    'details': response.text
                }), 500
                
        except requests.exceptions.ConnectionError:
            return jsonify({
                'success': False,
                'error': 'Could not connect to AI model. Please make sure Ollama is running locally.',
                'fallback_response': "I'm sorry, but I'm currently unable to connect to the AI service. Please try again later or contact support if the issue persists."
            }), 503
            
        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'AI model response timeout',
                'fallback_response': "I'm taking longer than usual to respond. Please try asking your question again."
            }), 504
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@chat_bp.route('/api/chat/health', methods=['GET'])
def chat_health():
    """Check if Ollama service is available"""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_available = any(model.get('name', '').startswith(MODEL_NAME) for model in models)
            
            return jsonify({
                'ollama_available': True,
                'model_available': model_available,
                'model_name': MODEL_NAME,
                'status': 'healthy' if model_available else 'model_not_found'
            })
        else:
            return jsonify({
                'ollama_available': False,
                'model_available': False,
                'status': 'ollama_error'
            })
    except requests.exceptions.ConnectionError:
        return jsonify({
            'ollama_available': False,
            'model_available': False,
            'status': 'connection_error'
        })
    except Exception as e:
        return jsonify({
            'ollama_available': False,
            'model_available': False,
            'status': 'error',
            'error': str(e)
        })

@chat_bp.route('/api/chat/suggestions', methods=['GET'])
def chat_suggestions():
    """Get suggested questions for the user"""
    suggestions = [
        "How can I create a better budget?",
        "What are some tips for saving money?",
        "How do I track my expenses effectively?",
        "What FinGuard features should I use first?",
        "Help me understand my spending habits",
        "How can I set financial goals?",
        "What's the best way to categorize expenses?",
        "How often should I review my budget?"
    ]
    
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })
