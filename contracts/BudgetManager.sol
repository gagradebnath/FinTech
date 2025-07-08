// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "./FinGuardToken.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title BudgetManager
 * @dev Smart contract for budget management and spending limits
 */
contract BudgetManager is Ownable {
    FinGuardToken public finguardToken;
    
    struct Budget {
        uint256 id;
        address user;
        string category;
        uint256 allocatedAmount;
        uint256 spentAmount;
        uint256 startDate;
        uint256 endDate;
        bool isActive;
    }
    
    struct SpendingRecord {
        uint256 budgetId;
        uint256 amount;
        string description;
        uint256 timestamp;
    }
    
    mapping(uint256 => Budget) public budgets;
    mapping(address => uint256[]) public userBudgets;
    mapping(string => uint256[]) public categoryBudgets;
    mapping(uint256 => SpendingRecord[]) public budgetSpending;
    
    uint256 public nextBudgetId;
    
    event BudgetCreated(
        uint256 indexed budgetId,
        address indexed user,
        string category,
        uint256 allocatedAmount,
        uint256 startDate,
        uint256 endDate
    );
    
    event BudgetUpdated(uint256 indexed budgetId, uint256 newAllocatedAmount);
    event SpendingRecorded(uint256 indexed budgetId, uint256 amount, string description);
    event BudgetExceeded(uint256 indexed budgetId, uint256 overspentAmount);
    event BudgetCompleted(uint256 indexed budgetId);
    
    constructor(address _tokenAddress) {
        finguardToken = FinGuardToken(_tokenAddress);
        nextBudgetId = 1;
    }
    
    /**
     * @dev Create a new budget
     */
    function createBudget(
        address user,
        string memory category,
        uint256 allocatedAmount,
        uint256 duration // in seconds
    ) external returns (uint256) {
        require(allocatedAmount > 0, "Allocated amount must be greater than zero");
        require(duration > 0, "Duration must be greater than zero");
        
        uint256 budgetId = nextBudgetId++;
        uint256 startDate = block.timestamp;
        uint256 endDate = startDate + duration;
        
        budgets[budgetId] = Budget({
            id: budgetId,
            user: user,
            category: category,
            allocatedAmount: allocatedAmount,
            spentAmount: 0,
            startDate: startDate,
            endDate: endDate,
            isActive: true
        });
        
        userBudgets[user].push(budgetId);
        categoryBudgets[category].push(budgetId);
        
        emit BudgetCreated(budgetId, user, category, allocatedAmount, startDate, endDate);
        
        return budgetId;
    }
    
    /**
     * @dev Check if spending is within budget limits
     */
    function checkBudgetLimits(
        address user,
        string memory category,
        uint256 amount
    ) external view returns (bool withinLimit, uint256 availableAmount, uint256 budgetId) {
        uint256[] memory userBudgetIds = userBudgets[user];
        
        for (uint256 i = 0; i < userBudgetIds.length; i++) {
            Budget memory budget = budgets[userBudgetIds[i]];
            
            if (
                budget.isActive &&
                keccak256(abi.encodePacked(budget.category)) == keccak256(abi.encodePacked(category)) &&
                block.timestamp >= budget.startDate &&
                block.timestamp <= budget.endDate
            ) {
                uint256 available = budget.allocatedAmount - budget.spentAmount;
                
                if (amount <= available) {
                    return (true, available, budget.id);
                } else {
                    return (false, available, budget.id);
                }
            }
        }
        
        // No active budget found for this category
        return (true, type(uint256).max, 0);
    }
    
    /**
     * @dev Record spending against a budget
     */
    function recordSpending(
        uint256 budgetId,
        uint256 amount,
        string memory description
    ) external {
        Budget storage budget = budgets[budgetId];
        require(budget.id != 0, "Budget does not exist");
        require(budget.isActive, "Budget is not active");
        require(block.timestamp <= budget.endDate, "Budget period has ended");
        
        budget.spentAmount += amount;
        
        budgetSpending[budgetId].push(SpendingRecord({
            budgetId: budgetId,
            amount: amount,
            description: description,
            timestamp: block.timestamp
        }));
        
        emit SpendingRecorded(budgetId, amount, description);
        
        // Check if budget is exceeded
        if (budget.spentAmount > budget.allocatedAmount) {
            uint256 overspentAmount = budget.spentAmount - budget.allocatedAmount;
            emit BudgetExceeded(budgetId, overspentAmount);
        }
        
        // Check if budget is fully spent
        if (budget.spentAmount >= budget.allocatedAmount) {
            budget.isActive = false;
            emit BudgetCompleted(budgetId);
        }
    }
    
    /**
     * @dev Update budget allocation
     */
    function updateBudgetAllocation(uint256 budgetId, uint256 newAllocatedAmount) external {
        Budget storage budget = budgets[budgetId];
        require(budget.id != 0, "Budget does not exist");
        require(budget.user == msg.sender || msg.sender == owner(), "Not authorized");
        require(newAllocatedAmount > 0, "Allocated amount must be greater than zero");
        
        budget.allocatedAmount = newAllocatedAmount;
        
        // Reactivate budget if it was completed but now has more allocation
        if (!budget.isActive && budget.spentAmount < newAllocatedAmount) {
            budget.isActive = true;
        }
        
        emit BudgetUpdated(budgetId, newAllocatedAmount);
    }
    
    /**
     * @dev Get budget details
     */
    function getBudget(uint256 budgetId) external view returns (
        uint256 id,
        address user,
        string memory category,
        uint256 allocatedAmount,
        uint256 spentAmount,
        uint256 startDate,
        uint256 endDate,
        bool isActive
    ) {
        Budget memory budget = budgets[budgetId];
        return (
            budget.id,
            budget.user,
            budget.category,
            budget.allocatedAmount,
            budget.spentAmount,
            budget.startDate,
            budget.endDate,
            budget.isActive
        );
    }
    
    /**
     * @dev Get user's budgets
     */
    function getUserBudgets(address user) external view returns (uint256[] memory) {
        return userBudgets[user];
    }
    
    /**
     * @dev Get spending history for a budget
     */
    function getBudgetSpending(uint256 budgetId) external view returns (
        uint256[] memory amounts,
        string[] memory descriptions,
        uint256[] memory timestamps
    ) {
        SpendingRecord[] memory spending = budgetSpending[budgetId];
        uint256 length = spending.length;
        
        amounts = new uint256[](length);
        descriptions = new string[](length);
        timestamps = new uint256[](length);
        
        for (uint256 i = 0; i < length; i++) {
            amounts[i] = spending[i].amount;
            descriptions[i] = spending[i].description;
            timestamps[i] = spending[i].timestamp;
        }
        
        return (amounts, descriptions, timestamps);
    }
    
    /**
     * @dev Get budget utilization percentage
     */
    function getBudgetUtilization(uint256 budgetId) external view returns (uint256) {
        Budget memory budget = budgets[budgetId];
        require(budget.id != 0, "Budget does not exist");
        
        if (budget.allocatedAmount == 0) {
            return 0;
        }
        
        return (budget.spentAmount * 100) / budget.allocatedAmount;
    }
    
    /**
     * @dev Deactivate a budget
     */
    function deactivateBudget(uint256 budgetId) external {
        Budget storage budget = budgets[budgetId];
        require(budget.id != 0, "Budget does not exist");
        require(budget.user == msg.sender || msg.sender == owner(), "Not authorized");
        
        budget.isActive = false;
    }
}
