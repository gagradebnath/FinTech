"""
Solidity Blockchain Integration for FinGuard
Web3 Python interface for smart contracts
"""

from web3 import Web3
from eth_account import Account
import json
import os
from flask import current_app
from typing import Dict, List, Tuple, Optional

class SolidityBlockchain:
    """Web3 integration for FinGuard smart contracts"""
    
    def __init__(self):
        self.w3 = None
        self.contracts = {}
        self.accounts = {}
        self.is_connected = False
        
    def connect(self, rpc_url: str = "http://127.0.0.1:8545"):
        """Connect to Ethereum node"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))
            self.is_connected = self.w3.is_connected()
            
            if self.is_connected:
                print(f"✅ Connected to Ethereum node at {rpc_url}")
                print(f"📊 Chain ID: {self.w3.eth.chain_id}")
                print(f"💰 Latest block: {self.w3.eth.block_number}")
            else:
                print(f"❌ Failed to connect to Ethereum node at {rpc_url}")
                
            return self.is_connected
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def load_contracts(self, deployment_file: str = "deployment-info.json"):
        """Load deployed contract addresses and ABIs"""
        try:
            # Load deployment info
            with open(deployment_file, 'r') as f:
                deployment_info = json.load(f)
            
            # Load contract ABIs
            abi_files = {
                'FinGuardToken': 'artifacts/contracts/FinGuardToken.sol/FinGuardToken.json',
                'TransactionManager': 'artifacts/contracts/TransactionManager.sol/TransactionManager.json',
                'BudgetManager': 'artifacts/contracts/BudgetManager.sol/BudgetManager.json'
            }
            
            for contract_name, address in deployment_info['contracts'].items():
                if contract_name in abi_files:
                    with open(abi_files[contract_name], 'r') as f:
                        artifact = json.load(f)
                        abi = artifact['abi']
                    
                    self.contracts[contract_name] = {
                        'address': address,
                        'contract': self.w3.eth.contract(address=address, abi=abi),
                        'abi': abi
                    }
                    print(f"✅ Loaded {contract_name} at {address}")
            
            # Load test accounts
            for account_info in deployment_info.get('testAccounts', []):
                self.accounts[account_info['userId']] = account_info['address']
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading contracts: {e}")
            return False
    
    def get_account_balance(self, user_id: str) -> Dict:
        """Get user's ETH and token balances"""
        if user_id not in self.accounts:
            return {"error": "User not found"}
        
        address = self.accounts[user_id]
        
        try:
            # Get ETH balance
            eth_balance = self.w3.eth.get_balance(address)
            eth_balance_ether = self.w3.from_wei(eth_balance, 'ether')
            
            # Get FGT token balance
            token_contract = self.contracts['FinGuardToken']['contract']
            token_balance = token_contract.functions.balanceOf(address).call()
            token_balance_ether = self.w3.from_wei(token_balance, 'ether')
            
            return {
                "address": address,
                "eth_balance": float(eth_balance_ether),
                "fgt_balance": float(token_balance_ether),
                "eth_balance_wei": eth_balance,
                "fgt_balance_wei": token_balance
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_transaction(self, sender_id: str, receiver_id: str, amount: float, 
                          transaction_type: str, note: str, location: str = "") -> Dict:
        """Create a blockchain transaction"""
        if not self.is_connected:
            return {"success": False, "error": "Not connected to blockchain"}
        
        try:
            sender_address = self.accounts.get(sender_id)
            receiver_address = self.accounts.get(receiver_id)
            
            if not sender_address or not receiver_address:
                return {"success": False, "error": "User address not found"}
            
            # Convert amount to Wei
            amount_wei = self.w3.to_wei(amount, 'ether')
            
            # Get transaction manager contract
            tx_manager = self.contracts['TransactionManager']['contract']
            
            # Create transaction
            tx_hash = tx_manager.functions.createTransaction(
                receiver_address,
                amount_wei,
                transaction_type,
                note,
                location
            ).transact({'from': sender_address})
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Get transaction ID from event logs
            tx_id = None
            for log in receipt.logs:
                try:
                    decoded_log = tx_manager.events.TransactionCreated().processLog(log)
                    tx_id = decoded_log['args']['transactionId']
                    break
                except:
                    continue
            
            return {
                "success": True,
                "transaction_hash": receipt.transactionHash.hex(),
                "transaction_id": tx_id,
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def execute_transaction(self, transaction_id: int, executor_id: str) -> Dict:
        """Execute a pending transaction"""
        try:
            executor_address = self.accounts.get(executor_id)
            if not executor_address:
                return {"success": False, "error": "Executor address not found"}
            
            tx_manager = self.contracts['TransactionManager']['contract']
            
            # Execute transaction
            tx_hash = tx_manager.functions.executeTransaction(
                transaction_id
            ).transact({'from': executor_address})
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "success": True,
                "transaction_hash": receipt.transactionHash.hex(),
                "gas_used": receipt.gasUsed,
                "block_number": receipt.blockNumber
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_budget_limits(self, user_id: str, category: str, amount: float) -> Dict:
        """Check if spending is within budget limits"""
        try:
            user_address = self.accounts.get(user_id)
            if not user_address:
                return {"error": "User address not found"}
            
            amount_wei = self.w3.to_wei(amount, 'ether')
            budget_manager = self.contracts['BudgetManager']['contract']
            
            result = budget_manager.functions.checkBudgetLimits(
                user_address, category, amount_wei
            ).call()
            
            return {
                "within_limit": result[0],
                "available_amount": float(self.w3.from_wei(result[1], 'ether')),
                "budget_id": result[2] if result[2] != 0 else None
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def create_budget(self, user_id: str, category: str, amount: float, duration_days: int) -> Dict:
        """Create a new budget"""
        try:
            user_address = self.accounts.get(user_id)
            if not user_address:
                return {"success": False, "error": "User address not found"}
            
            amount_wei = self.w3.to_wei(amount, 'ether')
            duration_seconds = duration_days * 24 * 60 * 60
            
            budget_manager = self.contracts['BudgetManager']['contract']
            
            tx_hash = budget_manager.functions.createBudget(
                user_address,
                category,
                amount_wei,
                duration_seconds
            ).transact({'from': user_address})
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Get budget ID from event logs
            budget_id = None
            for log in receipt.logs:
                try:
                    decoded_log = budget_manager.events.BudgetCreated().processLog(log)
                    budget_id = decoded_log['args']['budgetId']
                    break
                except:
                    continue
            
            return {
                "success": True,
                "budget_id": budget_id,
                "transaction_hash": receipt.transactionHash.hex()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_transaction_details(self, transaction_id: int) -> Dict:
        """Get transaction details"""
        try:
            tx_manager = self.contracts['TransactionManager']['contract']
            result = tx_manager.functions.getTransaction(transaction_id).call()
            
            return {
                "id": result[0],
                "sender": result[1],
                "receiver": result[2],
                "amount": float(self.w3.from_wei(result[3], 'ether')),
                "transaction_type": result[4],
                "note": result[5],
                "timestamp": result[6],
                "is_executed": result[7],
                "is_reverted": result[8]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def get_user_budgets(self, user_id: str) -> List[Dict]:
        """Get user's budgets"""
        try:
            user_address = self.accounts.get(user_id)
            if not user_address:
                return []
            
            budget_manager = self.contracts['BudgetManager']['contract']
            budget_ids = budget_manager.functions.getUserBudgets(user_address).call()
            
            budgets = []
            for budget_id in budget_ids:
                budget_data = budget_manager.functions.getBudget(budget_id).call()
                utilization = budget_manager.functions.getBudgetUtilization(budget_id).call()
                
                budgets.append({
                    "id": budget_data[0],
                    "user": budget_data[1],
                    "category": budget_data[2],
                    "allocated_amount": float(self.w3.from_wei(budget_data[3], 'ether')),
                    "spent_amount": float(self.w3.from_wei(budget_data[4], 'ether')),
                    "start_date": budget_data[5],
                    "end_date": budget_data[6],
                    "is_active": budget_data[7],
                    "utilization_percent": utilization
                })
            
            return budgets
            
        except Exception as e:
            print(f"Error getting user budgets: {e}")
            return []
    
    def get_blockchain_stats(self) -> Dict:
        """Get blockchain statistics"""
        if not self.is_connected:
            return {"error": "Not connected to blockchain"}
        
        try:
            stats = {
                "connected": True,
                "chain_id": self.w3.eth.chain_id,
                "latest_block": self.w3.eth.block_number,
                "gas_price": self.w3.eth.gas_price,
                "accounts_loaded": len(self.accounts),
                "contracts_loaded": len(self.contracts)
            }
            
            # Get token statistics
            if 'FinGuardToken' in self.contracts:
                token_contract = self.contracts['FinGuardToken']['contract']
                total_supply = token_contract.functions.totalSupply().call()
                stats["token_total_supply"] = float(self.w3.from_wei(total_supply, 'ether'))
            
            return stats
            
        except Exception as e:
            return {"error": str(e)}

# Global Solidity blockchain instance
solidity_blockchain = SolidityBlockchain()
