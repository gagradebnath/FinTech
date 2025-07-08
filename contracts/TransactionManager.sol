// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./FinGuardToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title TransactionManager
 * @dev Manages all financial transactions in FinGuard system
 */
contract TransactionManager is Ownable, ReentrancyGuard, Pausable {
    FinGuardToken public finguardToken;
    
    struct Transaction {
        uint256 id;
        address sender;
        address receiver;
        uint256 amount;
        string transactionType;
        string note;
        string location;
        uint256 timestamp;
        bool isExecuted;
        bool isReverted;
    }
    
    struct User {
        address walletAddress;
        string userId;
        uint256 balance;
        bool isActive;
        bool isAgent;
        uint256 dailyLimit;
        uint256 dailySpent;
        uint256 lastResetDay;
    }
    
    mapping(uint256 => Transaction) public transactions;
    mapping(address => User) public users;
    mapping(string => address) public userIdToAddress;
    mapping(address => bool) public authorizedAgents;
    mapping(address => bool) public flaggedAddresses;
    
    uint256 public nextTransactionId;
    uint256 public transactionFee = 1 * 10**15; // 0.001 ETH
    uint256 public constant MAX_DAILY_LIMIT = 10000 * 10**18; // 10,000 tokens
    
    event TransactionCreated(
        uint256 indexed transactionId,
        address indexed sender,
        address indexed receiver,
        uint256 amount,
        string transactionType
    );
    
    event TransactionExecuted(uint256 indexed transactionId);
    event TransactionReverted(uint256 indexed transactionId);
    event UserRegistered(address indexed userAddress, string userId);
    event AgentAuthorized(address indexed agent);
    event AddressFlagged(address indexed flaggedAddress);
    event DailyLimitUpdated(address indexed user, uint256 newLimit);
    
    constructor(address _tokenAddress) {
        finguardToken = FinGuardToken(_tokenAddress);
        nextTransactionId = 1;
    }
    
    /**
     * @dev Register a new user
     */
    function registerUser(
        string memory userId,
        address userAddress,
        uint256 dailyLimit,
        bool isAgent
    ) external onlyOwner {
        require(userIdToAddress[userId] == address(0), "User ID already exists");
        require(users[userAddress].walletAddress == address(0), "Address already registered");
        require(dailyLimit <= MAX_DAILY_LIMIT, "Daily limit exceeds maximum");
        
        users[userAddress] = User({
            walletAddress: userAddress,
            userId: userId,
            balance: 0,
            isActive: true,
            isAgent: isAgent,
            dailyLimit: dailyLimit,
            dailySpent: 0,
            lastResetDay: block.timestamp / 1 days
        });
        
        userIdToAddress[userId] = userAddress;
        
        if (isAgent) {
            authorizedAgents[userAddress] = true;
            emit AgentAuthorized(userAddress);
        }
        
        emit UserRegistered(userAddress, userId);
    }
    
    /**
     * @dev Create a new transaction
     */
    function createTransaction(
        address receiver,
        uint256 amount,
        string memory transactionType,
        string memory note,
        string memory location
    ) external whenNotPaused nonReentrant returns (uint256) {
        require(users[msg.sender].isActive, "Sender not registered or inactive");
        require(users[receiver].isActive, "Receiver not registered or inactive");
        require(!flaggedAddresses[msg.sender], "Sender address is flagged");
        require(!flaggedAddresses[receiver], "Receiver address is flagged");
        require(amount > 0, "Amount must be greater than zero");
        
        // Check daily limit
        _checkDailyLimit(msg.sender, amount);
        
        // Check balance
        require(finguardToken.balanceOf(msg.sender) >= amount, "Insufficient balance");
        
        uint256 transactionId = nextTransactionId++;
        
        transactions[transactionId] = Transaction({
            id: transactionId,
            sender: msg.sender,
            receiver: receiver,
            amount: amount,
            transactionType: transactionType,
            note: note,
            location: location,
            timestamp: block.timestamp,
            isExecuted: false,
            isReverted: false
        });
        
        emit TransactionCreated(transactionId, msg.sender, receiver, amount, transactionType);
        
        return transactionId;
    }
    
    /**
     * @dev Execute a transaction
     */
    function executeTransaction(uint256 transactionId) external nonReentrant {
        Transaction storage txn = transactions[transactionId];
        require(txn.id != 0, "Transaction does not exist");
        require(!txn.isExecuted, "Transaction already executed");
        require(!txn.isReverted, "Transaction was reverted");
        require(
            msg.sender == txn.sender || authorizedAgents[msg.sender] || msg.sender == owner(),
            "Not authorized to execute transaction"
        );
        
        // Execute the token transfer
        require(
            finguardToken.transferFrom(txn.sender, txn.receiver, txn.amount),
            "Token transfer failed"
        );
        
        // Update user balances
        users[txn.sender].balance = finguardToken.balanceOf(txn.sender);
        users[txn.receiver].balance = finguardToken.balanceOf(txn.receiver);
        
        // Update daily spent amount
        _updateDailySpent(txn.sender, txn.amount);
        
        txn.isExecuted = true;
        
        emit TransactionExecuted(transactionId);
    }
    
    /**
     * @dev Revert a transaction (only by authorized agents or owner)
     */
    function revertTransaction(uint256 transactionId) external {
        require(
            authorizedAgents[msg.sender] || msg.sender == owner(),
            "Not authorized to revert transaction"
        );
        
        Transaction storage txn = transactions[transactionId];
        require(txn.id != 0, "Transaction does not exist");
        require(txn.isExecuted, "Transaction not executed yet");
        require(!txn.isReverted, "Transaction already reverted");
        
        // Reverse the token transfer
        require(
            finguardToken.transferFrom(txn.receiver, txn.sender, txn.amount),
            "Token transfer reversal failed"
        );
        
        // Update user balances
        users[txn.sender].balance = finguardToken.balanceOf(txn.sender);
        users[txn.receiver].balance = finguardToken.balanceOf(txn.receiver);
        
        txn.isReverted = true;
        
        emit TransactionReverted(transactionId);
    }
    
    /**
     * @dev Flag an address for suspicious activity
     */
    function flagAddress(address addressToFlag) external {
        require(
            authorizedAgents[msg.sender] || msg.sender == owner(),
            "Not authorized to flag addresses"
        );
        
        flaggedAddresses[addressToFlag] = true;
        emit AddressFlagged(addressToFlag);
    }
    
    /**
     * @dev Update user's daily limit
     */
    function updateDailyLimit(address user, uint256 newLimit) external onlyOwner {
        require(users[user].walletAddress != address(0), "User not registered");
        require(newLimit <= MAX_DAILY_LIMIT, "Daily limit exceeds maximum");
        
        users[user].dailyLimit = newLimit;
        emit DailyLimitUpdated(user, newLimit);
    }
    
    /**
     * @dev Check daily spending limit
     */
    function _checkDailyLimit(address user, uint256 amount) internal {
        User storage userData = users[user];
        uint256 currentDay = block.timestamp / 1 days;
        
        // Reset daily spent if it's a new day
        if (currentDay > userData.lastResetDay) {
            userData.dailySpent = 0;
            userData.lastResetDay = currentDay;
        }
        
        require(
            userData.dailySpent + amount <= userData.dailyLimit,
            "Daily spending limit exceeded"
        );
    }
    
    /**
     * @dev Update daily spent amount
     */
    function _updateDailySpent(address user, uint256 amount) internal {
        users[user].dailySpent += amount;
    }
    
    /**
     * @dev Get transaction details
     */
    function getTransaction(uint256 transactionId) external view returns (
        uint256 id,
        address sender,
        address receiver,
        uint256 amount,
        string memory transactionType,
        string memory note,
        uint256 timestamp,
        bool isExecuted,
        bool isReverted
    ) {
        Transaction memory txn = transactions[transactionId];
        return (
            txn.id,
            txn.sender,
            txn.receiver,
            txn.amount,
            txn.transactionType,
            txn.note,
            txn.timestamp,
            txn.isExecuted,
            txn.isReverted
        );
    }
    
    /**
     * @dev Get user details
     */
    function getUser(address userAddress) external view returns (
        string memory userId,
        uint256 balance,
        bool isActive,
        bool isAgent,
        uint256 dailyLimit,
        uint256 dailySpent
    ) {
        User memory user = users[userAddress];
        return (
            user.userId,
            user.balance,
            user.isActive,
            user.isAgent,
            user.dailyLimit,
            user.dailySpent
        );
    }
    
    /**
     * @dev Emergency pause
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause
     */
    function unpause() external onlyOwner {
        _unpause();
    }
}
