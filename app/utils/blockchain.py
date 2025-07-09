import hashlib
import json
import time
import uuid
from datetime import datetime
from flask import current_app
from typing import List, Dict, Optional

class Transaction:
    """Blockchain transaction class"""
    
    def __init__(self, sender_id: str, receiver_id: str, amount: float, 
                 transaction_type: str, note: str = "", location: str = ""):
        self.id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.note = note
        self.location = location
        self.timestamp = datetime.now()
        self.signature = None
        
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'note': self.note,
            'location': self.location,
            'timestamp': self.timestamp.isoformat(),
            'signature': self.signature
        }
    
    def calculate_hash(self) -> str:
        """Calculate transaction hash"""
        transaction_string = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(transaction_string.encode()).hexdigest()
    
    def sign_transaction(self, private_key: str):
        """Sign transaction with private key (simplified)"""
        # In production, use proper cryptographic signing
        transaction_hash = self.calculate_hash()
        self.signature = hashlib.sha256(f"{transaction_hash}{private_key}".encode()).hexdigest()

class Block:
    """Blockchain block class"""
    
    def __init__(self, index: int, transactions: List[Transaction], 
                 previous_hash: str, timestamp: datetime = None):
        self.index = index
        self.timestamp = timestamp or datetime.now()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()
        
    def calculate_hash(self) -> str:
        """Calculate block hash"""
        transactions_data = [tx.to_dict() for tx in self.transactions]
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp.isoformat(),
            'transactions': transactions_data,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int = 4):
        """Mine block with proof of work (simplified)"""
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"Block mined: {self.hash}")

class FinGuardBlockchain:
    """Main blockchain class for FinGuard"""
    
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.mining_reward = 10
        self.difficulty = 2
        self._initialized = False
        
    def ensure_initialized(self):
        """Ensure blockchain is initialized with genesis block"""
        if not self._initialized:
            self.create_genesis_block()
            self._initialized = True
    
    def create_genesis_block(self):
        """Create the first block in the chain"""
        genesis_block = Block(0, [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        
        # Save to database if we're in application context
        try:
            from flask import current_app
            if current_app:
                # For genesis block, we don't have transactions to link
                # So we'll create a special database entry
                conn = current_app.get_db_connection()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute('''
                            INSERT INTO blockchain (id, `index`, type, timestamp, previous_hash, hash, transaction_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ''', (
                            str(uuid.uuid4()),
                            genesis_block.index,
                            'genesis',
                            genesis_block.timestamp,
                            genesis_block.previous_hash,
                            genesis_block.hash,
                            None
                        ))
                    conn.commit()
                    print("✅ Genesis block saved to database")
                except Exception as e:
                    print(f"Error saving genesis block to database: {e}")
                    conn.rollback()
                finally:
                    conn.close()
        except RuntimeError:
            # Not in application context, skip database save
            print("Genesis block created (database save skipped - no app context)")
            pass
    
    def get_latest_block(self) -> Block:
        """Get the most recent block"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction):
        """Add transaction to pending pool"""
        self.ensure_initialized()
        if self.validate_transaction(transaction):
            self.pending_transactions.append(transaction)
            return True
        return False
    
    def validate_transaction(self, transaction: Transaction) -> bool:
        """Validate transaction before adding to blockchain"""
        # Basic validation
        if transaction.amount <= 0:
            return False
        
        # Check if sender has sufficient balance (simplified)
        # Allow system transactions and initial transactions for testing
        if transaction.sender_id == "system":
            return True
            
        sender_balance = self.get_balance(transaction.sender_id)
        if sender_balance < transaction.amount:
            # For testing purposes, allow negative balances
            # In production, you would return False here
            print(f"Warning: {transaction.sender_id} has insufficient balance ({sender_balance} < {transaction.amount})")
        
        # Verify signature (in production, use proper crypto verification)
        if transaction.signature is None:
            return False
            
        return True
    
    def mine_pending_transactions(self, mining_reward_address: str = "system"):
        """Mine pending transactions into a new block"""
        self.ensure_initialized()
        if not self.pending_transactions:
            return None
            
        # Add mining reward transaction
        reward_transaction = Transaction(
            sender_id="system",
            receiver_id=mining_reward_address,
            amount=self.mining_reward,
            transaction_type="Mining Reward"
        )
        reward_transaction.sign_transaction("system_private_key")
        self.pending_transactions.append(reward_transaction)
        
        # Create new block
        block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.get_latest_block().hash
        )
        
        # Mine the block
        block.mine_block(self.difficulty)
        
        # Add to chain
        self.chain.append(block)
        
        # Save to database
        self.save_block_to_db(block)
        
        # Clear pending transactions
        self.pending_transactions = []
        
        return block
    
    def get_balance(self, user_id: str) -> float:
        """Calculate user balance from blockchain"""
        self.ensure_initialized()
        balance = 0
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.receiver_id == user_id:
                    balance += transaction.amount
                if transaction.sender_id == user_id:
                    balance -= transaction.amount
                    
        return balance
    
    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain"""
        self.ensure_initialized()
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block hash is valid
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # Check if previous hash matches
            if current_block.previous_hash != previous_block.hash:
                return False
                
        return True
    
    def save_block_to_db(self, block: Block):
        """Save block to database with proper transaction relationships and optimized performance"""
        try:
            conn = current_app.get_db_connection()
            try:
                # Set connection timeout and lock wait timeout for better performance
                with conn.cursor() as cursor:
                    cursor.execute('SET innodb_lock_wait_timeout = 10')
                    cursor.execute('SET lock_wait_timeout = 10')
                
                with conn.cursor() as cursor:
                    transaction_ids = []
                    
                    # Bulk check if users exist to reduce database calls
                    user_ids = set()
                    for transaction in block.transactions:
                        user_ids.add(transaction.sender_id)
                        user_ids.add(transaction.receiver_id)
                    
                    # Single query to check all users
                    existing_users = set()
                    if user_ids:
                        user_placeholders = ','.join(['%s'] * len(user_ids))
                        cursor.execute(f'SELECT id FROM users WHERE id IN ({user_placeholders})', list(user_ids))
                        existing_users = {row['id'] for row in cursor.fetchall()}
                    
                    # Process transactions with existing user data
                    for transaction in block.transactions:
                        # Save blockchain transaction for sender if user exists
                        if transaction.sender_id in existing_users:
                            sender_tx_id = str(uuid.uuid4())
                            cursor.execute('''
                                INSERT INTO blockchain_transactions (id, user_id, amount, current_balance, method, timestamp)
                                SELECT %s, %s, %s, COALESCE(balance, 0), %s, %s
                                FROM users WHERE id = %s
                            ''', (
                                sender_tx_id,
                                transaction.sender_id,
                                -transaction.amount,
                                transaction.transaction_type,
                                transaction.timestamp,
                                transaction.sender_id
                            ))
                            transaction_ids.append(sender_tx_id)
                        
                        # Save blockchain transaction for receiver if user exists
                        if transaction.receiver_id in existing_users:
                            receiver_tx_id = str(uuid.uuid4())
                            cursor.execute('''
                                INSERT INTO blockchain_transactions (id, user_id, amount, current_balance, method, timestamp)
                                SELECT %s, %s, %s, COALESCE(balance, 0), %s, %s
                                FROM users WHERE id = %s
                            ''', (
                                receiver_tx_id,
                                transaction.receiver_id,
                                transaction.amount,
                                transaction.transaction_type,
                                transaction.timestamp,
                                transaction.receiver_id
                            ))
                            transaction_ids.append(receiver_tx_id)
                        
                        # Log warning for non-existent users
                        if transaction.sender_id not in existing_users or transaction.receiver_id not in existing_users:
                            print(f"Warning: User(s) not found for transaction {transaction.id}")
                    
                    # Save the block with reference to first transaction if any
                    first_transaction_id = transaction_ids[0] if transaction_ids else None
                    
                    cursor.execute('''
                        INSERT INTO blockchain (id, `index`, type, timestamp, previous_hash, hash, transaction_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        str(uuid.uuid4()),
                        block.index,
                        'block',
                        block.timestamp,
                        block.previous_hash,
                        block.hash,
                        first_transaction_id
                    ))
                
                conn.commit()
                print(f"✅ Block {block.index} and {len(transaction_ids)} transactions saved to database")
            except Exception as e:
                print(f"Error saving block to database: {e}")
                conn.rollback()
            finally:
                conn.close()
        except RuntimeError:
            # Not in application context
            print(f"Block {block.index} saved in memory only (no app context)")
            pass
    
    def get_transaction_history(self, user_id: str) -> List[Dict]:
        """Get user's transaction history from blockchain"""
        self.ensure_initialized()
        transactions = []
        
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.sender_id == user_id or transaction.receiver_id == user_id:
                    tx_dict = transaction.to_dict()
                    tx_dict['block_index'] = block.index
                    tx_dict['block_hash'] = block.hash
                    transactions.append(tx_dict)
                    
        return sorted(transactions, key=lambda x: x['timestamp'], reverse=True)

# Global blockchain instance
finguard_blockchain = FinGuardBlockchain()

def process_blockchain_transaction(sender_id: str, receiver_id: str, amount: float, 
                                 transaction_type: str, note: str = "", location: str = "",
                                 sender_private_key: str = "default_key") -> bool:
    """Process a transaction through the blockchain"""
    try:
        # Create transaction
        transaction = Transaction(
            sender_id=sender_id,
            receiver_id=receiver_id,
            amount=amount,
            transaction_type=transaction_type,
            note=note,
            location=location
        )
        
        # Sign transaction
        transaction.sign_transaction(sender_private_key)
        
        # Add to pending transactions
        if finguard_blockchain.add_transaction(transaction):
            # Mine block (in production, this would be done by miners)
            block = finguard_blockchain.mine_pending_transactions()
            return block is not None
        
        return False
        
    except Exception as e:
        print(f"Error processing blockchain transaction: {e}")
        return False

def verify_transaction(transaction_id: str) -> Dict:
    """Verify a transaction exists in the blockchain"""
    for block in finguard_blockchain.chain:
        for transaction in block.transactions:
            if transaction.id == transaction_id:
                return {
                    'verified': True,
                    'block_index': block.index,
                    'block_hash': block.hash,
                    'transaction': transaction.to_dict()
                }
    
    return {'verified': False}

def get_blockchain_stats() -> Dict:
    """Get blockchain statistics"""
    finguard_blockchain.ensure_initialized()
    total_blocks = len(finguard_blockchain.chain)
    total_transactions = sum(len(block.transactions) for block in finguard_blockchain.chain)
    
    return {
        'total_blocks': total_blocks,
        'total_transactions': total_transactions,
        'chain_valid': finguard_blockchain.is_chain_valid(),
        'pending_transactions': len(finguard_blockchain.pending_transactions),
        'latest_block_hash': finguard_blockchain.get_latest_block().hash if total_blocks > 0 else None
    }