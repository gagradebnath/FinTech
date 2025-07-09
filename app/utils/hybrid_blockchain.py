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
                    # Load contracts and accounts for the reloader
                    if self.solidity_blockchain.load_contracts():
                        self.solidity_available = True
                        print(f"✅ Solidity blockchain available (cached) - {len(self.solidity_blockchain.accounts)} accounts loaded")
                    else:
                        print("⚠️ Solidity blockchain cache failed to load contracts")
                else:
                    print("⚠️ Solidity blockchain cache connection failed")
            except Exception as e:
                print(f"⚠️ Solidity blockchain cache failed: {e}")
            return
            
        try:
            print("🚀 Initializing Solidity blockchain...")
            self.solidity_blockchain = SolidityBlockchain()
            # Try to connect and load contracts
            if self.solidity_blockchain.connect():
                print("✅ Solidity blockchain connected")
                if self.solidity_blockchain.load_contracts():
                    self.solidity_available = True
                    print(f"✅ Solidity blockchain available - {len(self.solidity_blockchain.accounts)} accounts loaded")
                else:
                    print("⚠️ Solidity blockchain connected but contracts not loaded")
            else:
                print("⚠️ Solidity blockchain connection failed")
        except Exception as e:
            print(f"⚠️ Solidity blockchain initialization failed: {e}")
            import traceback
            traceback.print_exc()
    
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
                users_registered = self._ensure_users_registered([sender_id, receiver_id])
                
                if users_registered:
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
                        error_msg = tx_result.get('error', 'Unknown error')
                        results["errors"].append(f"Solidity blockchain error: {error_msg}")
                        print(f"⚠️ Solidity blockchain transaction failed: {error_msg}")
                else:
                    results["errors"].append("Solidity blockchain error: Users not registered")
                    print("⚠️ Solidity blockchain transaction skipped: Users not registered")
            except Exception as e:
                results["errors"].append(f"Solidity blockchain error: {e}")
                print(f"❌ Solidity blockchain error: {e}")
        else:
            print("ℹ️ Solidity blockchain not available, using Python blockchain only")
        
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
            print("⚠️ Solidity blockchain not available")
            return False
            
        print(f"🔍 Checking if users are registered: {user_ids}")
        
        # First, check if we have accounts loaded - if not, try to reload them
        if not self.solidity_blockchain.accounts:
            print("🔄 No accounts loaded in Solidity blockchain, attempting to reload...")
            try:
                if self.solidity_blockchain.reload_accounts():
                    print(f"✅ Reloaded {len(self.solidity_blockchain.accounts)} accounts")
                else:
                    print("❌ Failed to reload accounts")
                    return False
            except Exception as e:
                print(f"❌ Exception during account reload: {e}")
                return False
        
        # Check if the specific users we need are in the loaded accounts
        missing_users = [user_id for user_id in user_ids if user_id not in self.solidity_blockchain.accounts]
        
        if missing_users:
            print(f"⚠️ Users not found in Solidity accounts: {missing_users}")
            # Try reloading accounts one more time
            print("🔄 Attempting to reload accounts for missing users...")
            try:
                if self.solidity_blockchain.reload_accounts():
                    print(f"✅ Reloaded {len(self.solidity_blockchain.accounts)} accounts")
                    # Check again
                    still_missing = [user_id for user_id in missing_users if user_id not in self.solidity_blockchain.accounts]
                    if still_missing:
                        print(f"❌ Users still missing after reload: {still_missing}")
                        return False
                    else:
                        print("✅ All users found after reload")
                        return True
                else:
                    print("❌ Failed to reload accounts for missing users")
                    return False
            except Exception as e:
                print(f"❌ Exception during second reload attempt: {e}")
                return False
        
        print(f"✅ All required users found in Solidity blockchain: {user_ids}")
        return True
    
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
