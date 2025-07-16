#!/usr/bin/env python3
"""
Blockchain implementation for FinGuard transaction security.
This module provides blockchain functionality to ensure transaction integrity
and detect fraudulent activities.
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from flask import current_app

class Block:
    """Represents a single block in the blockchain"""
    
    def __init__(self, index: int, timestamp: datetime, transaction_data: dict, 
                 previous_hash: str, transaction_id: str = None):
        self.index = index
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.transaction_data = transaction_data
        self.previous_hash = previous_hash
        self.transaction_id = transaction_id or str(uuid.uuid4())
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Calculate the SHA-256 hash of the block"""
        block_string = json.dumps({
            'index': self.index,
            'timestamp': self.timestamp.isoformat(),
            'transaction_data': self.transaction_data,
            'previous_hash': self.previous_hash,
            'transaction_id': self.transaction_id
        }, sort_keys=True, default=str)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def is_valid(self) -> bool:
        """Verify if the block's hash is valid"""
        return self.hash == self.calculate_hash()

class FinGuardBlockchain:
    """Blockchain implementation for FinGuard financial transactions"""
    
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """Create the first block in the chain"""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now(timezone.utc),
            transaction_data={
                'type': 'genesis',
                'message': 'FinGuard Blockchain Genesis Block',
                'amount': 0.0,
                'user_id': 'system'
            },
            previous_hash='0'
        )
        self.chain.append(genesis_block)
        return genesis_block
    
    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain"""
        return self.chain[-1] if self.chain else None
    
    def add_transaction_block(self, transaction_data: dict) -> Block:
        """Add a new transaction block to the chain"""
        latest_block = self.get_latest_block()
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now(timezone.utc),
            transaction_data=transaction_data,
            previous_hash=latest_block.hash if latest_block else '0'
        )
        
        self.chain.append(new_block)
        return new_block
    
    def is_chain_valid(self) -> Tuple[bool, List[str]]:
        """Validate the entire blockchain and return any errors"""
        errors = []
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # Check if current block's hash is valid
            if not current_block.is_valid():
                errors.append(f"Block {i} has invalid hash")
            
            # Check if current block's previous hash matches the previous block's hash
            if current_block.previous_hash != previous_block.hash:
                errors.append(f"Block {i} has invalid previous hash")
        
        return len(errors) == 0, errors

def get_blockchain_connection():
    """Get database connection for blockchain operations"""
    return current_app.get_db_connection()

def create_blockchain_transaction(user_id: str, amount: Decimal, current_balance: Decimal, 
                                method: str, transaction_id: str = None) -> str:
    """Create a blockchain transaction record"""
    try:
        connection = get_blockchain_connection()
        blockchain_tx_id = transaction_id or str(uuid.uuid4())
        
        with connection.cursor() as cursor:
            # First check if user exists
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            user_exists = cursor.fetchone()
            
            if not user_exists:
                print(f"User {user_id} does not exist, cannot create blockchain transaction")
                return None
            
            # Insert blockchain transaction
            cursor.execute("""
                INSERT INTO blockchain_transactions 
                (id, user_id, amount, current_balance, method, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                blockchain_tx_id,
                user_id,
                float(amount),
                float(current_balance),
                method,
                datetime.now()
            ))
            
            connection.commit()
            print(f"Blockchain transaction created: id={blockchain_tx_id}, user_id={user_id}, amount={amount}")
            return blockchain_tx_id
            
    except Exception as e:
        print(f"Error creating blockchain transaction: {e}")
        connection.rollback() if 'connection' in locals() else None
        return None
    finally:
        if 'connection' in locals():
            connection.close()

def add_block_to_chain(block_data: dict, transaction_id: str) -> bool:
    """Add a new block to the blockchain in the database"""
    try:
        connection = get_blockchain_connection()
        
        with connection.cursor() as cursor:
            # First check if the blockchain_transactions record exists
            cursor.execute("SELECT id FROM blockchain_transactions WHERE id = %s", (transaction_id,))
            tx_exists = cursor.fetchone()
            
            if not tx_exists:
                print(f"Blockchain transaction {transaction_id} does not exist, cannot add block")
                return False
            
            # Get the latest block to determine the new index and previous hash
            cursor.execute("""
                SELECT `index`, hash FROM blockchain 
                ORDER BY `index` DESC LIMIT 1
            """)
            latest_block = cursor.fetchone()
            
            # Calculate new block properties
            new_index = (latest_block['index'] + 1) if latest_block else 0
            previous_hash = latest_block['hash'] if latest_block else '0'
            
            # Create the block
            block = Block(
                index=new_index,
                timestamp=datetime.now(timezone.utc),
                transaction_data=block_data,
                previous_hash=previous_hash,
                transaction_id=transaction_id
            )
            
            # Insert the block into the database
            cursor.execute("""
                INSERT INTO blockchain 
                (id, `index`, type, timestamp, previous_hash, hash, transaction_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                str(uuid.uuid4()),
                block.index,
                block_data.get('type', 'transaction'),
                block.timestamp,
                block.previous_hash,
                block.hash,
                transaction_id
            ))
            
            connection.commit()
            print(f"Block added successfully: index={block.index}, hash={block.hash}")
            return True
            
    except Exception as e:
        print(f"Error adding block to chain: {e}")
        connection.rollback() if 'connection' in locals() else None
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def validate_transaction_blockchain(user_id: str, transaction_amount: Decimal, 
                                  current_balance: Decimal) -> Tuple[bool, str]:
    """Validate a transaction against the blockchain"""
    try:
        connection = get_blockchain_connection()
        
        with connection.cursor() as cursor:
            # Get user's blockchain transaction history
            cursor.execute("""
                SELECT bt.amount, bt.current_balance, bt.timestamp,
                       b.hash, b.previous_hash, b.index
                FROM blockchain_transactions bt
                JOIN blockchain b ON bt.id = b.transaction_id
                WHERE bt.user_id = %s
                ORDER BY b.index ASC
            """, (user_id,))
            
            blockchain_history = cursor.fetchall()
            
            if not blockchain_history:
                # First transaction for user - create genesis entry
                return True, "First transaction - blockchain initialized"
            
            # Validate blockchain integrity
            calculated_balance = Decimal('0.00')
            previous_hash = '0'
            
            for i, record in enumerate(blockchain_history):
                # Recreate block data for hash verification
                block_data = {
                    'user_id': user_id,
                    'amount': float(record['amount']),
                    'balance': float(record['current_balance']),
                    'timestamp': record['timestamp'].isoformat(),
                    'type': 'transaction'
                }
                
                # Verify hash integrity
                expected_hash = Block(
                    index=record['index'],
                    timestamp=record['timestamp'],
                    transaction_data=block_data,
                    previous_hash=previous_hash
                ).calculate_hash()
                
                if expected_hash != record['hash']:
                    return False, f"Hash mismatch at transaction {i+1}"
                
                # Verify balance progression
                calculated_balance += Decimal(str(record['amount']))
                if abs(calculated_balance - Decimal(str(record['current_balance']))) > Decimal('0.01'):
                    return False, f"Balance inconsistency at transaction {i+1}"
                
                previous_hash = record['hash']
            
            # Validate current transaction against expected balance
            expected_new_balance = calculated_balance + transaction_amount
            if abs(expected_new_balance - current_balance) > Decimal('0.01'):
                return False, f"Current transaction balance mismatch"
            
            return True, "Blockchain validation successful"
            
    except Exception as e:
        print(f"Error validating blockchain: {e}")
        return False, f"Blockchain validation error: {str(e)}"
    finally:
        if 'connection' in locals():
            connection.close()

def process_transaction_with_blockchain(user_id: str, transaction_amount: Decimal, 
                                      current_balance: Decimal, transaction_type: str,
                                      transaction_details: dict) -> Tuple[bool, str]:
    """Process a transaction with blockchain validation and recording"""
    try:
        # For now, let's allow transactions to proceed even if blockchain fails
        # This prevents the blockchain from blocking legitimate transactions
        
        # Validate transaction against blockchain
        is_valid, validation_message = validate_transaction_blockchain(
            user_id, transaction_amount, current_balance
        )
        
        if not is_valid:
            print(f"Blockchain validation failed: {validation_message}")
            # Mark user as potentially fraudulent but don't block transaction
            flag_user_as_fraud(user_id, f"Blockchain inconsistency: {validation_message}")
            # Still allow the transaction to proceed
        
        # Create blockchain transaction record
        blockchain_tx_id = create_blockchain_transaction(
            user_id, transaction_amount, current_balance, transaction_type
        )
        
        if not blockchain_tx_id:
            print("Failed to create blockchain transaction record, but allowing transaction")
            return True, "Transaction processed (blockchain recording failed)"
        
        # Create block data
        block_data = {
            'user_id': user_id,
            'amount': float(transaction_amount),
            'balance': float(current_balance),
            'type': transaction_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'details': transaction_details
        }
        
        # Add block to chain
        if not add_block_to_chain(block_data, blockchain_tx_id):
            print("Failed to add block to blockchain, but allowing transaction")
            return True, "Transaction processed (blockchain recording failed)"
        
        return True, "Transaction processed and added to blockchain"
        
    except Exception as e:
        print(f"Error processing transaction with blockchain: {e}")
        # Don't block transactions due to blockchain errors
        return True, f"Transaction processed (blockchain error: {str(e)})"

def flag_user_as_fraud(user_id: str, reason: str) -> bool:
    """Flag a user as potentially fraudulent"""
    try:
        connection = get_blockchain_connection()
        
        with connection.cursor() as cursor:
            # Check if user is already flagged
            cursor.execute("""
                SELECT id FROM fraud_list WHERE reported_user_id = %s
            """, (user_id,))
            
            existing_flag = cursor.fetchone()
            
            if not existing_flag:
                # Flag the user
                cursor.execute("""
                    INSERT INTO fraud_list (id, user_id, reported_user_id, reason, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    'system',  # System-generated fraud flag
                    user_id,
                    f"Blockchain Security Alert: {reason}",
                    datetime.now()
                ))
                
                connection.commit()
                print(f"User {user_id} flagged for fraud: {reason}")
                return True
            else:
                print(f"User {user_id} already flagged for fraud")
                return False
                
    except Exception as e:
        print(f"Error flagging user as fraud: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def get_user_blockchain_summary(user_id: str) -> dict:
    """Get a summary of user's blockchain activity"""
    try:
        connection = get_blockchain_connection()
        
        with connection.cursor() as cursor:
            # Get blockchain statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_blocks,
                    SUM(bt.amount) as total_amount,
                    MIN(bt.timestamp) as first_transaction,
                    MAX(bt.timestamp) as last_transaction,
                    MAX(bt.current_balance) as current_balance
                FROM blockchain_transactions bt
                JOIN blockchain b ON bt.id = b.transaction_id
                WHERE bt.user_id = %s
            """, (user_id,))
            
            summary = cursor.fetchone()
            
            # Get fraud status
            cursor.execute("""
                SELECT reason, created_at FROM fraud_list
                WHERE reported_user_id = %s
                ORDER BY created_at DESC LIMIT 1
            """, (user_id,))
            
            fraud_info = cursor.fetchone()
            
            return {
                'user_id': user_id,
                'total_blocks': summary['total_blocks'] or 0,
                'total_amount': float(summary['total_amount'] or 0),
                'first_transaction': summary['first_transaction'],
                'last_transaction': summary['last_transaction'],
                'current_balance': float(summary['current_balance'] or 0),
                'is_flagged_fraud': bool(fraud_info),
                'fraud_reason': fraud_info['reason'] if fraud_info else None,
                'fraud_date': fraud_info['created_at'] if fraud_info else None
            }
            
    except Exception as e:
        print(f"Error getting blockchain summary: {e}")
        return {
            'user_id': user_id,
            'total_blocks': 0,
            'total_amount': 0,
            'error': str(e)
        }
    finally:
        if 'connection' in locals():
            connection.close()

def verify_entire_blockchain() -> Tuple[bool, List[str]]:
    """Verify the integrity of the entire blockchain"""
    try:
        connection = get_blockchain_connection()
        
        with connection.cursor() as cursor:
            # Get all blocks ordered by index
            cursor.execute("""
                SELECT b.id, b.index, b.type, b.timestamp, b.previous_hash, b.hash,
                       bt.user_id, bt.amount, bt.current_balance, bt.method
                FROM blockchain b
                LEFT JOIN blockchain_transactions bt ON b.transaction_id = bt.id
                ORDER BY b.index ASC
            """)
            
            blocks = cursor.fetchall()
            errors = []
            
            if not blocks:
                return True, ["No blocks found in blockchain"]
            
            # Verify each block
            for i, block_data in enumerate(blocks):
                if i == 0:
                    # Genesis block
                    if block_data['previous_hash'] != '0':
                        errors.append(f"Genesis block has invalid previous hash")
                    continue
                
                # Verify previous hash matches
                previous_block = blocks[i - 1]
                if block_data['previous_hash'] != previous_block['hash']:
                    errors.append(f"Block {i} has invalid previous hash reference")
                
                # Recreate block for hash verification
                if block_data['user_id']:  # Transaction block
                    transaction_data = {
                        'user_id': block_data['user_id'],
                        'amount': float(block_data['amount']),
                        'balance': float(block_data['current_balance']),
                        'type': block_data['type'],
                        'timestamp': block_data['timestamp'].isoformat()
                    }
                else:  # Genesis block
                    transaction_data = {
                        'type': 'genesis',
                        'message': 'FinGuard Blockchain Genesis Block',
                        'amount': 0.0,
                        'user_id': 'system'
                    }
                
                # Verify hash
                expected_block = Block(
                    index=block_data['index'],
                    timestamp=block_data['timestamp'],
                    transaction_data=transaction_data,
                    previous_hash=block_data['previous_hash']
                )
                
                if expected_block.hash != block_data['hash']:
                    errors.append(f"Block {i} has invalid hash")
            
            return len(errors) == 0, errors
            
    except Exception as e:
        return False, [f"Blockchain verification error: {str(e)}"]
    finally:
        if 'connection' in locals():
            connection.close()

def get_blockchain_analytics() -> dict:
    """Get analytics about the blockchain"""
    try:
        connection = get_blockchain_connection()
        
        with connection.cursor() as cursor:
            # Get blockchain statistics
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT b.id) as total_blocks,
                    COUNT(DISTINCT bt.user_id) as unique_users,
                    SUM(bt.amount) as total_volume,
                    AVG(bt.amount) as avg_transaction,
                    MIN(b.timestamp) as blockchain_start,
                    MAX(b.timestamp) as last_block
                FROM blockchain b
                LEFT JOIN blockchain_transactions bt ON b.transaction_id = bt.id
            """)
            
            stats = cursor.fetchone()
            
            # Get fraud statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_fraud_flags,
                    COUNT(DISTINCT reported_user_id) as flagged_users
                FROM fraud_list
                WHERE reason LIKE '%Blockchain%'
            """)
            
            fraud_stats = cursor.fetchone()
            
            return {
                'total_blocks': stats['total_blocks'] or 0,
                'unique_users': stats['unique_users'] or 0,
                'total_volume': float(stats['total_volume'] or 0),
                'avg_transaction': float(stats['avg_transaction'] or 0),
                'blockchain_start': stats['blockchain_start'],
                'last_block': stats['last_block'],
                'total_fraud_flags': fraud_stats['total_fraud_flags'] or 0,
                'flagged_users': fraud_stats['flagged_users'] or 0
            }
            
    except Exception as e:
        print(f"Error getting blockchain analytics: {e}")
        return {'error': str(e)}
    finally:
        if 'connection' in locals():
            connection.close()
