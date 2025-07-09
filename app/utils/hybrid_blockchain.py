"""
Hybrid Blockchain Utility for FinGuard
Supports both Python blockchain and Solidity blockchain
"""

from flask import current_app
from .blockchain import process_blockchain_transaction
from .solidity_blockchain import SolidityBlockchain
import json

class HybridBlockchain:
    """Manages both Python and Solidity blockchain implementations"""
    
    def __init__(self):
        self.python_blockchain = True  # Always available
        self.solidity_blockchain = None
        self.solidity_available = False
        self._init_solidity()
    
    def _init_solidity(self):
        """Initialize Solidity blockchain if available"""
        # Skip initialization if we're in a Flask reloader subprocess
        import os
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            # This is the reloader subprocess, skip detailed initialization
            print("🔄 Flask reloader detected - using cached Solidity connection")
            try:
                self.solidity_blockchain = SolidityBlockchain()
                if self.solidity_blockchain.connect():
                    self.solidity_available = True
                    print("✅ Solidity blockchain available (cached)")
            except Exception as e:
                print(f"⚠️ Solidity blockchain cache failed: {e}")
            return
            
        try:
            self.solidity_blockchain = SolidityBlockchain()
            # Try to connect and load contracts
            if self.solidity_blockchain.connect():
                if self.solidity_blockchain.load_contracts():
                    self.solidity_available = True
                    print("✅ Solidity blockchain available")
                else:
                    print("⚠️ Solidity blockchain connected but contracts not loaded")
            else:
                print("⚠️ Solidity blockchain connection failed")
        except Exception as e:
            print(f"⚠️ Solidity blockchain initialization failed: {e}")
    
    def process_transaction(self, sender_id, receiver_id, amount, transaction_type, note, location):
        """Process transaction using available blockchain(s)"""
        from flask import current_app
        import uuid
        
        results = {
            "python_blockchain": False,
            "solidity_blockchain": False,
            "errors": [],
            "blockchain_tx_id": None,
            "solidity_tx_hash": None,
            "solidity_tx_id": None
        }
        
        # Always try Python blockchain first (for database consistency)
        try:
            results["python_blockchain"] = process_blockchain_transaction(
                sender_id, receiver_id, amount, transaction_type, note, location
            )
            if results["python_blockchain"]:
                print("✅ Transaction recorded in Python blockchain")
        except Exception as e:
            results["errors"].append(f"Python blockchain error: {e}")
            print(f"❌ Python blockchain error: {e}")
        
        # Try Solidity blockchain if available
        if self.solidity_available:
            try:
                # First ensure users are registered in Solidity blockchain
                self._ensure_users_registered([sender_id, receiver_id])
                
                tx_result = self.solidity_blockchain.create_transaction(
                    sender_id, receiver_id, amount, transaction_type, note, location
                )
                results["solidity_blockchain"] = tx_result.get("success", False)
                if results["solidity_blockchain"]:
                    results["solidity_tx_hash"] = tx_result["transaction_hash"]
                    results["solidity_tx_id"] = tx_result.get("transaction_id")
                    
                    # Update blockchain_transactions table with Solidity details
                    self._update_blockchain_tables(
                        sender_id, receiver_id, amount, transaction_type, 
                        note, location, tx_result
                    )
                    
                    print(f"✅ Transaction recorded in Solidity blockchain: {tx_result['transaction_hash']}")
                else:
                    results["errors"].append(f"Solidity blockchain error: {tx_result.get('error', 'Unknown error')}")
            except Exception as e:
                results["errors"].append(f"Solidity blockchain error: {e}")
                print(f"❌ Solidity blockchain error: {e}")
        
        return results
    
    def _update_blockchain_tables(self, sender_id, receiver_id, amount, transaction_type, note, location, solidity_result):
        """Update blockchain_transactions table with Solidity transaction details"""
        from flask import current_app
        import uuid
        
        try:
            conn = current_app.get_db_connection()
            
            # Set shorter timeouts for blockchain operations
            with conn.cursor() as cursor:
                cursor.execute('SET innodb_lock_wait_timeout = 5')
                cursor.execute('SET lock_wait_timeout = 5')
            
            with conn.cursor() as cursor:
                # Create blockchain transaction records for both sender and receiver
                
                # Sender blockchain transaction record
                sender_blockchain_tx_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO blockchain_transactions 
                    (id, user_id, amount, current_balance, method, timestamp) 
                    VALUES (%s, %s, %s, 
                        (SELECT COALESCE(balance, 0) FROM users WHERE id = %s), 
                        %s, NOW())
                ''', (sender_blockchain_tx_id, sender_id, -amount, sender_id, 'solidity_debit'))
                
                # Receiver blockchain transaction record  
                receiver_blockchain_tx_id = str(uuid.uuid4())
                cursor.execute('''
                    INSERT INTO blockchain_transactions 
                    (id, user_id, amount, current_balance, method, timestamp) 
                    VALUES (%s, %s, %s, 
                        (SELECT COALESCE(balance, 0) FROM users WHERE id = %s), 
                        %s, NOW())
                ''', (receiver_blockchain_tx_id, receiver_id, amount, receiver_id, 'solidity_credit'))
                
                # Create blockchain records for the transaction
                sender_block_id = str(uuid.uuid4())
                receiver_block_id = str(uuid.uuid4())
                
                # Get the latest block index safely
                cursor.execute('SELECT MAX(`index`) as max_index FROM blockchain')
                result = cursor.fetchone()
                next_index = (result['max_index'] if result and result['max_index'] is not None else -1) + 1
                
                # Sender block
                cursor.execute('''
                    INSERT INTO blockchain 
                    (id, `index`, type, timestamp, previous_hash, hash, transaction_id) 
                    VALUES (%s, %s, %s, NOW(), %s, %s, %s)
                ''', (
                    sender_block_id, 
                    next_index, 
                    f"solidity_{transaction_type}_debit",
                    solidity_result.get("transaction_hash", "")[:255],
                    solidity_result.get("transaction_hash", ""),
                    sender_blockchain_tx_id
                ))
                
                # Receiver block
                cursor.execute('''
                    INSERT INTO blockchain 
                    (id, `index`, type, timestamp, previous_hash, hash, transaction_id) 
                    VALUES (%s, %s, %s, NOW(), %s, %s, %s)
                ''', (
                    receiver_block_id, 
                    next_index + 1, 
                    f"solidity_{transaction_type}_credit",
                    solidity_result.get("transaction_hash", ""),
                    solidity_result.get("transaction_hash", ""),
                    receiver_blockchain_tx_id
                ))
                
                conn.commit()
                print(f"✅ Updated blockchain tables with Solidity transaction data")
                
        except Exception as e:
            print(f"❌ Error updating blockchain tables: {e}")
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'conn' in locals():
                conn.close()
    
    def _ensure_users_registered(self, user_ids):
        """Ensure users are registered in Solidity blockchain"""
        if not self.solidity_available:
            return
            
        try:
            from flask import current_app
            conn = current_app.get_db_connection()
            
            with conn.cursor() as cursor:
                # Get user details for registration
                user_placeholders = ','.join(['%s'] * len(user_ids))
                cursor.execute(f'''
                    SELECT u.id, u.first_name, u.last_name, c.email, c.phone
                    FROM users u
                    LEFT JOIN contact_info c ON u.id = c.user_id
                    WHERE u.id IN ({user_placeholders})
                ''', user_ids)
                
                users = cursor.fetchall()
                
            conn.close()
            
            # Register each user in Solidity blockchain if not already registered
            for user in users:
                try:
                    # Check if user exists in Solidity blockchain
                    user_exists = self.solidity_blockchain.get_account_balance(user['id'])
                    
                    if user_exists.get('error') == 'User address not found':
                        # Register the user
                        registration_result = self.solidity_blockchain.register_user(
                            user['id'],
                            user.get('first_name', ''),
                            user.get('last_name', ''),
                            user.get('email', ''),
                            user.get('phone', '')
                        )
                        
                        if registration_result.get('success'):
                            print(f"✅ User {user['id']} registered in Solidity blockchain")
                        else:
                            print(f"⚠️ Failed to register user {user['id']} in Solidity blockchain: {registration_result.get('error')}")
                    
                except Exception as e:
                    print(f"⚠️ Error checking/registering user {user['id']} in Solidity blockchain: {e}")
                    
        except Exception as e:
            print(f"⚠️ Error ensuring users are registered: {e}")

    def get_blockchain_status(self):
        """Get status of both blockchain implementations"""
        return {
            "python_blockchain": self.python_blockchain,
            "solidity_blockchain": self.solidity_available,
            "solidity_connected": self.solidity_blockchain.is_connected if self.solidity_blockchain else False
        }
    
    def get_user_balance(self, user_id):
        """Get user balance from Solidity blockchain if available"""
        if self.solidity_available:
            return self.solidity_blockchain.get_account_balance(user_id)
        return {"error": "Solidity blockchain not available"}
    
    def check_budget_limits(self, user_id, category, amount):
        """Check budget limits using Solidity blockchain if available"""
        if self.solidity_available:
            return self.solidity_blockchain.check_budget_limits(user_id, category, amount)
        return {"error": "Solidity blockchain not available"}

# Global instance
hybrid_blockchain = HybridBlockchain()
