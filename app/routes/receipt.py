from flask import Blueprint, request, jsonify, render_template, session, current_app
import requests
import json
import os
import uuid
from datetime import datetime
from PIL import Image
import pytesseract
from io import BytesIO
import base64
from .user import get_current_user
from app.utils.jwt_auth import get_current_user_from_jwt
from app.utils.transaction_utils import add_transaction
import re
import platform

# Configure pytesseract for Windows
if platform.system() == 'Windows':
    # Common installation paths for Tesseract on Windows
    possible_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', '')),
        r'C:\tesseract\tesseract.exe'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

receipt_bp = Blueprint('receipt', __name__)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "llama3.2:3b"

# Configure upload folder
UPLOAD_FOLDER = 'uploads/receipts'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(image_file):
    """Extract text from image using OCR"""
    try:
        # Open image using PIL
        image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Use pytesseract to extract text
        extracted_text = pytesseract.image_to_string(image)
        
        return extracted_text.strip()
    except Exception as e:
        current_app.logger.error(f"OCR Error: {str(e)}")
        return None

def process_receipt_with_nlp(ocr_text, user_id):
    """Process OCR text with Ollama to extract transaction data"""
    try:
        # Create a detailed prompt for extracting transaction information
        system_prompt = """You are a financial data extraction AI. Analyze the provided receipt text and extract transaction information in JSON format.

Extract the following information:
1. amount: The total amount spent (as a float number, no currency symbols)
2. payment_method: How the payment was made (Cash, Credit Card, Debit Card, etc.)
3. merchant_name: Name of the store/business 
4. location: Address or location of the business
5. category: Type of expense (Food, Groceries, Transportation, Shopping, Entertainment, Healthcare, etc.)
6. date: Transaction date in YYYY-MM-DD format (if not found, use today's date)
7. time: Transaction time in HH:MM format (if not found, use current time)
8. items: List of purchased items with their prices (if clearly identifiable)

Rules:
- Return ONLY valid JSON format
- If information is not clearly available, use reasonable defaults
- For amount, extract the TOTAL amount (usually the largest amount on receipt)
- For payment_method, if not specified, default to "Unknown"
- For category, analyze the items/merchant to determine the most appropriate category
- Be conservative with amounts - only extract if you're confident it's the total

Example response:
{
    "amount": 25.67,
    "payment_method": "Credit Card",
    "merchant_name": "Walmart Supercenter",
    "location": "123 Main St, City, State",
    "category": "Groceries",
    "date": "2024-01-15",
    "time": "14:30",
    "items": [
        {"name": "Milk", "price": 3.99},
        {"name": "Bread", "price": 2.50}
    ]
}"""

        user_prompt = f"""Please analyze this receipt text and extract transaction information:

{ocr_text}

Return the information in the exact JSON format specified."""

        # Prepare the request to Ollama
        ollama_request = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for more consistent extraction
                "max_tokens": 1000
            }
        }

        # Send request to Ollama with increased timeout and better error handling
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=ollama_request,
                timeout=90  # Increased timeout to 90 seconds
            )
            
            if response.status_code == 200:
                ollama_response = response.json()
                ai_response = ollama_response.get('message', {}).get('content', '')
                
                # Try to extract JSON from the response
                try:
                    # Find JSON in the response
                    json_start = ai_response.find('{')
                    json_end = ai_response.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_str = ai_response[json_start:json_end]
                        transaction_data = json.loads(json_str)
                        
                        # Validate and clean the data
                        cleaned_data = {
                            'amount': float(transaction_data.get('amount', 0.0)),
                            'payment_method': transaction_data.get('payment_method', 'Unknown'),
                            'merchant_name': transaction_data.get('merchant_name', 'Unknown Merchant'),
                            'location': transaction_data.get('location', 'Unknown Location'),
                            'category': transaction_data.get('category', 'Other'),
                            'date': transaction_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                            'time': transaction_data.get('time', datetime.now().strftime('%H:%M')),
                            'items': transaction_data.get('items', [])
                        }
                        
                        current_app.logger.info(f"Successfully extracted transaction data: {cleaned_data}")
                        return cleaned_data
                    else:
                        current_app.logger.error("No valid JSON found in AI response")
                        return create_fallback_transaction(ocr_text, "Invalid AI response format")
                        
                except json.JSONDecodeError as e:
                    current_app.logger.error(f"Failed to parse AI response as JSON: {e}")
                    return create_fallback_transaction(ocr_text, "Failed to parse AI response")
            else:
                current_app.logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return create_fallback_transaction(ocr_text, f"AI service error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            current_app.logger.error("Ollama request timed out after 90 seconds")
            return create_fallback_transaction(ocr_text, "AI processing timed out")
        except requests.exceptions.ConnectionError:
            current_app.logger.error("Failed to connect to Ollama service at " + OLLAMA_BASE_URL)
            return create_fallback_transaction(ocr_text, "AI service unavailable")
        except Exception as e:
            current_app.logger.error(f"Unexpected error during AI processing: {str(e)}")
            return create_fallback_transaction(ocr_text, f"AI processing error: {str(e)}")
            
    except Exception as e:
        current_app.logger.error(f"NLP processing error: {str(e)}")
        return create_fallback_transaction(ocr_text, f"NLP processing failed: {str(e)}")


def create_fallback_transaction(ocr_text, error_reason="AI processing failed"):
    """
    Create a fallback transaction when AI processing fails
    """
    import re
    
    # Try to extract basic information using simple text processing
    amount = extract_amount_from_text(ocr_text)
    merchant = extract_merchant_from_text(ocr_text)
    
    fallback_data = {
        "amount": amount,
        "merchant_name": merchant,
        "category": "Other",
        "date": datetime.now().strftime('%Y-%m-%d'),
        "time": datetime.now().strftime('%H:%M'),
        "location": "Unknown Location",
        "payment_method": "Unknown",
        "items": [],
        "note": f"Fallback extraction used ({error_reason}). Please review and edit all fields."
    }
    
    current_app.logger.info(f"Created fallback transaction: {fallback_data}")
    return fallback_data


def extract_amount_from_text(text):
    """Extract amount using regex patterns"""
    import re
    
    # Look for common price patterns
    patterns = [
        r'\$\s*(\d+\.\d{2})',  # $XX.XX
        r'total\s*:?\s*\$?\s*(\d+\.\d{2})',  # Total: $XX.XX
        r'amount\s*:?\s*\$?\s*(\d+\.\d{2})',  # Amount: $XX.XX
        r'(\d+\.\d{2})\s*$',  # XX.XX at end of line
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                # Return the largest amount found (likely the total)
                return max([float(match) for match in matches])
            except ValueError:
                continue
    
    return 0.00


def extract_merchant_from_text(text):
    """Extract merchant name from text"""
    import re
    
    lines = text.strip().split('\n')
    if lines:
        # Usually the first line contains the merchant name
        first_line = lines[0].strip()
        # Clean up common OCR artifacts
        merchant = re.sub(r'[^\w\s]', '', first_line).strip()
        if len(merchant) > 3:  # Ensure it's not just noise
            return merchant[:50]  # Limit length
    
    return "Unknown Merchant"

@receipt_bp.route('/receipt-upload', methods=['GET'])
def receipt_upload_page():
    """Render the receipt upload interface"""
    return render_template('receipt_upload.html')

@receipt_bp.route('/api/receipt/upload', methods=['POST'])
def upload_receipt():
    """Handle receipt upload and processing"""
    try:
        # Get current user
        user = get_current_user_from_jwt()
        if not user:
            user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        # Check if file was uploaded
        if 'receipt' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['receipt']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload an image file.'}), 400

        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save the file temporarily
        file.save(file_path)
        
        try:
            # Extract text using OCR
            with open(file_path, 'rb') as img_file:
                ocr_text = extract_text_from_image(img_file)
            
            if not ocr_text:
                return jsonify({
                    'error': 'Could not extract text from the image. Please ensure the receipt is clear and readable.'
                }), 400
            
            # Process with NLP
            transaction_data = process_receipt_with_nlp(ocr_text, user['id'])
            
            if not transaction_data:
                # If AI processing completely fails, create a basic fallback
                transaction_data = create_fallback_transaction(ocr_text, "AI processing completely failed")
            
            # Always return success with the extracted data (whether from AI or fallback)
            current_app.logger.info(f"Processing complete: {transaction_data}")
            
            # Prepare transaction data for database
            transaction_id = str(uuid.uuid4())
            
            # Convert date and time to datetime
            try:
                date_str = transaction_data['date']
                time_str = transaction_data['time']
                timestamp = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            except ValueError:
                timestamp = datetime.now()
            
            # Create transaction note with receipt details
            note_parts = [
                f"Receipt from {transaction_data['merchant_name']}",
                f"Location: {transaction_data['location']}",
                f"Category: {transaction_data['category']}"
            ]
            
            if transaction_data['items']:
                note_parts.append("Items:")
                for item in transaction_data['items'][:5]:  # Limit to first 5 items
                    note_parts.append(f"- {item.get('name', 'Unknown')} ${item.get('price', '0.00')}")
            
            note = "\n".join(note_parts)
            
            # Add transaction to database
            try:
                add_transaction(
                    transaction_id=transaction_id,
                    amount=transaction_data['amount'],
                    payment_method=transaction_data['payment_method'],
                    timestamp=timestamp,
                    sender_id=user['id'],  # User is spending money
                    receiver_id=None,  # No specific receiver for purchases
                    note=note,
                    transaction_type='Payment',  # Receipt represents a payment/purchase
                    location=transaction_data['location']
                )
                
                return jsonify({
                    'success': True,
                    'message': 'Receipt processed successfully!',
                    'transaction_data': transaction_data,
                    'transaction_id': transaction_id,
                    'ocr_text': ocr_text
                })
                
            except Exception as db_error:
                current_app.logger.error(f"Database error: {str(db_error)}")
                return jsonify({
                    'error': 'Failed to save transaction to database.',
                    'details': str(db_error)
                }), 500
                
        finally:
            # Clean up the uploaded file
            try:
                os.remove(file_path)
            except:
                pass
                
    except Exception as e:
        current_app.logger.error(f"Receipt upload error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@receipt_bp.route('/api/receipt/save-transaction', methods=['POST'])
def save_edited_transaction():
    """Save the edited transaction data"""
    try:
        # Get current user
        user = get_current_user_from_jwt()
        if not user:
            user = get_current_user()
        
        if not user:
            return jsonify({'error': 'Authentication required'}), 401

        data = request.get_json()
        if not data:
            return jsonify({'error': 'Transaction data is required'}), 400

        # Validate required fields
        required_fields = ['amount', 'category', 'merchant_name', 'payment_method', 'date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field.replace("_", " ").title()} is required'}), 400

        # Validate amount
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Amount must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid amount format'}), 400

        # Generate transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Parse date and time
        try:
            date_str = data['date']
            time_str = data.get('time', datetime.now().strftime('%H:%M'))
            timestamp = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
        except ValueError:
            timestamp = datetime.now()

        # Create comprehensive note
        note_parts = [
            f"Receipt from {data['merchant_name']}",
            f"Category: {data['category']}"
        ]
        
        if data.get('location'):
            note_parts.append(f"Location: {data['location']}")
        
        if data.get('note'):
            note_parts.append(f"Notes: {data['note']}")
        
        # Add items if any
        items = data.get('items', [])
        if items:
            note_parts.append("Items purchased:")
            for item in items[:10]:  # Limit to first 10 items
                if item.get('name'):
                    price = item.get('price', 0)
                    note_parts.append(f"- {item['name']} ${price:.2f}")

        note = "\n".join(note_parts)

        # Add transaction to database
        try:
            add_transaction(
                transaction_id=transaction_id,
                amount=amount,
                payment_method=data['payment_method'],
                timestamp=timestamp,
                sender_id=user['id'],  # User is spending money
                receiver_id=None,  # No specific receiver for purchases
                note=note,
                transaction_type='Payment',  # Receipt represents a payment/purchase
                location=data.get('location', 'Unknown Location')
            )
            
            return jsonify({
                'success': True,
                'message': 'Transaction saved successfully!',
                'transaction_id': transaction_id
            })
            
        except Exception as db_error:
            current_app.logger.error(f"Database error: {str(db_error)}")
            return jsonify({
                'error': 'Failed to save transaction to database.',
                'details': str(db_error)
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Save transaction error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@receipt_bp.route('/api/receipt/health', methods=['GET'])
def receipt_health():
    """Check if OCR and AI services are available"""
    try:
        # Check Ollama availability
        ollama_available = False
        model_available = False
        ollama_error = None
        
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_available = True
                models = response.json().get('models', [])
                model_available = any(model.get('name', '').startswith(MODEL_NAME) for model in models)
                if not model_available:
                    available_models = [model.get('name', 'unknown') for model in models]
                    ollama_error = f"Model '{MODEL_NAME}' not found. Available models: {', '.join(available_models) if available_models else 'none'}"
            else:
                ollama_error = f"Ollama API returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            ollama_error = f"Cannot connect to Ollama at {OLLAMA_BASE_URL}. Is Ollama running?"
        except requests.exceptions.Timeout:
            ollama_error = "Ollama connection timed out"
        except Exception as e:
            ollama_error = f"Ollama error: {str(e)}"
        
        # Check OCR availability (pytesseract)
        ocr_available = False
        ocr_error = None
        
        try:
            # Test pytesseract with a simple image
            from PIL import Image
            import io
            
            # Create a simple test image with text
            test_img = Image.new('RGB', (200, 50), color='white')
            
            # Try to run OCR on the test image
            test_text = pytesseract.image_to_string(test_img)
            ocr_available = True
            
        except pytesseract.TesseractNotFoundError:
            ocr_error = "Tesseract executable not found. Please install Tesseract OCR."
        except Exception as e:
            ocr_error = f"OCR error: {str(e)}"
        
        return jsonify({
            'ocr_available': ocr_available,
            'ocr_error': ocr_error,
            'tesseract_path': getattr(pytesseract.pytesseract, 'tesseract_cmd', 'default'),
            'ollama_available': ollama_available,
            'ollama_error': ollama_error,
            'model_available': model_available,
            'model_name': MODEL_NAME,
            'ollama_url': OLLAMA_BASE_URL,
            'status': 'healthy' if (ocr_available and ollama_available and model_available) else 'partially_available'
        })
        
    except Exception as e:
        return jsonify({
            'ocr_available': False,
            'ocr_error': str(e),
            'tesseract_path': getattr(pytesseract.pytesseract, 'tesseract_cmd', 'default'),
            'ollama_available': False,
            'model_available': False,
            'status': 'error',
            'error': str(e)
        })
