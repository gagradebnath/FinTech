// Budget page dynamic JS

// Load saved budget when clicking the load button
document.addEventListener('DOMContentLoaded', function() {
    const loadBudgetBtn = document.getElementById('load-budget');
    const deleteBudgetBtn = document.getElementById('delete-budget');
    const savedBudgetsSelect = document.getElementById('saved-budgets');
    
    // Enable/disable delete button based on selection
    if (savedBudgetsSelect && deleteBudgetBtn) {
        savedBudgetsSelect.addEventListener('change', function() {
            deleteBudgetBtn.disabled = !this.value;
        });
    }
    
    if (loadBudgetBtn) {
        loadBudgetBtn.addEventListener('click', async function() {
            const budgetId = document.getElementById('saved-budgets').value;
            if (!budgetId) {
                alert('Please select a budget to load');
                return;
            }
            
            try {
                // Fetch the budget details from the server
                const response = await fetch(`/get_budget/${budgetId}`);
                const data = await response.json();
                
                if (data.success && data.budget) {
                    // Populate the form with the fetched budget data
                    populateFormWithBudgetData(data.budget);
                    // Update URL without reloading the page
                    history.pushState(null, '', `/plan-budget?budget_id=${budgetId}`);
                } else {
                    throw new Error(data.message || 'Failed to load budget');
                }
            } catch (error) {
                console.error('Error loading budget:', error);
                alert('Error: Could not load the selected budget. Please try again.');
            }
        });
    }
    
    // Delete budget functionality
    if (deleteBudgetBtn) {
        deleteBudgetBtn.addEventListener('click', async function() {
            const budgetId = document.getElementById('saved-budgets').value;
            if (!budgetId) {
                alert('Please select a budget to delete');
                return;
            }
            
            // Get the selected budget name for confirmation
            const selectedOption = document.querySelector(`#saved-budgets option[value="${budgetId}"]`);
            const budgetName = selectedOption ? selectedOption.textContent.split(' (')[0] : 'this budget';
            
            // Confirm deletion with reason
            const deleteConfirmed = confirm(`Are you sure you want to delete "${budgetName}"? This action cannot be undone.`);
            if (!deleteConfirmed) {
                return;
            }
            
            // Ask for deletion reason (optional)
            const deletionReason = prompt("Optional: Please provide a reason for deletion:", "User requested deletion");
            
            try {
                // Send delete request to the server
                const requestBody = deletionReason ? JSON.stringify({ reason: deletionReason }) : undefined;
                const headers = {
                    'Content-Type': 'application/json',
                };
                
                const response = await fetch(`/delete_budget/${budgetId}`, {
                    method: 'DELETE',
                    headers: headers,
                    body: requestBody
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Remove the option from the dropdown
                    selectedOption.remove();
                    
                    // Reset the form if the deleted budget was currently loaded
                    const currentBudgetId = new URLSearchParams(window.location.search).get('budget_id');
                    if (currentBudgetId === budgetId) {
                        // Clear the form
                        document.getElementById('budget-name').value = '';
                        document.getElementById('currency').value = '';
                        clearFormData();
                        // Update URL to remove budget_id parameter
                        history.pushState(null, '', '/plan-budget');
                    }
                    
                    // Disable delete button since no budget is selected
                    deleteBudgetBtn.disabled = true;
                    savedBudgetsSelect.value = '';
                    
                    // Show success message with timestamp if available
                    let successMessage = data.message || 'Budget deleted successfully!';
                    if (data.timestamp) {
                        successMessage += `\nDeleted at: ${new Date(data.timestamp).toLocaleString()}`;
                    }
                    alert(successMessage);
                    
                    // Log the deletion for debugging
                    console.log('Budget deleted:', {
                        budgetId: budgetId,
                        budgetName: budgetName,
                        reason: deletionReason,
                        timestamp: data.timestamp
                    });
                } else {
                    throw new Error(data.message || 'Failed to delete budget');
                }
            } catch (error) {
                console.error('Error deleting budget:', error);
                alert('Error: Could not delete the selected budget. Please try again.\n\nError details: ' + error.message);
            }
        });
    }
    
    // Check if we have pre-loaded budget data to populate the form
    const preloadedBudgetData = window.preloadedBudget;
    if (preloadedBudgetData) {
        populateFormWithBudgetData(preloadedBudgetData);
    }
});

// Function to populate the form with loaded budget data
function populateFormWithBudgetData(budgetData) {
    
    console.log('Populating form with budget data:', budgetData);
    
    // Set budget name and currency
    document.getElementById('budget-name').value = budgetData.name || '';
    document.getElementById('currency').value = budgetData.currency || '';
    
    // Clear existing income items (except the first one)
    const incomeList = document.getElementById('income-list');
    while (incomeList.children.length > 1) {
        incomeList.removeChild(incomeList.lastChild);
    }
    
    // Parse income sources
    let incomeSources = [];
    if (budgetData.income_source) {
        try {
            // Try to parse as JSON first
            incomeSources = JSON.parse(budgetData.income_source);
        } catch (e) {
            // If not JSON, split by comma
            const sources = budgetData.income_source.split(',');
            // Calculate an equal distribution of the total amount
            const equalShare = budgetData.amount / (sources.length || 1);
            
            incomeSources = sources.map(src => ({
                source: src.trim(),
                amount: equalShare
            }));
        }
    }
    
    // Populate first income item
    if (incomeSources.length > 0 && incomeList.children.length > 0) {
        const firstIncomeItem = incomeList.children[0];
        const sourceInput = firstIncomeItem.querySelector('input[type="text"]');
        const amountInput = firstIncomeItem.querySelector('input[type="number"]');
        
        if (sourceInput && amountInput) {
            sourceInput.value = incomeSources[0].source || '';
            amountInput.value = incomeSources[0].amount || budgetData.amount || '';
        }
        
        // Add additional income sources
        for (let i = 1; i < incomeSources.length; i++) {
            addIncomeItem(incomeSources[i].source, incomeSources[i].amount);
        }
    }
    
    // Clear existing expense categories
    const expenseList = document.getElementById('expense-list');
    expenseList.innerHTML = '';
    
    // Add expense categories and items
    if (budgetData.categories) {
        console.log('Adding categories:', budgetData.categories);
        Object.values(budgetData.categories).forEach(category => {
            console.log('Adding category:', category);
            addExpenseCategory(category.name, category.items);
        });
    }
    
    console.log('Form population complete');
}

// Helper function to add income item with data
function addIncomeItem(source, amount) {
    const incomeList = document.getElementById('income-list');
    const div = document.createElement('div');
    div.classList.add('row', 'g-2', 'income-item', 'mb-2');
    div.innerHTML = `
        <div class="col-md-6">
            <input type="text" class="form-control" placeholder="Income Source" value="${source || ''}" required>
        </div>
        <div class="col-md-4">
            <input type="number" class="form-control" placeholder="Amount" value="${amount || ''}" required>
        </div>
        <div class="col-md-2 d-grid">
            <button type="button" class="btn btn-danger remove-item">Remove</button>
        </div>
    `;
    incomeList.appendChild(div);
    div.querySelector('.remove-item').addEventListener('click', () => div.remove());
}

// Helper function to add expense category with data
function addExpenseCategory(categoryName, items) {
    const expenseList = document.getElementById('expense-list');
    const categoryDiv = document.createElement('div');
    categoryDiv.classList.add('expense-category', 'border', 'p-3', 'mb-3');
    
    // Ensure categoryName is a string and is one of the valid options
    const validCategoryName = typeof categoryName === 'string' && 
                              expenseCategoryOptions.includes(categoryName) ? 
                              categoryName : '';
    
    const optionsHtml = expenseCategoryOptions.map(opt => 
        `<option value="${opt}" ${opt === validCategoryName ? 'selected' : ''}>${opt}</option>`
    ).join('');
    
    categoryDiv.innerHTML = `
        <div class="mb-2">
            <select class="form-select expense-category-select" required>
                <option value="" disabled ${!validCategoryName ? 'selected' : ''}>Select Expense Category</option>
                ${optionsHtml}
            </select>
        </div>
        <div class="expense-items"></div>
        <button type="button" class="btn btn-sm btn-outline-success add-expense-item">+ Add Item</button>
        <button type="button" class="btn btn-sm btn-outline-danger remove-category">Remove Category</button>
    `;
    expenseList.appendChild(categoryDiv);
    
    // Add event listeners
    categoryDiv.querySelector('.add-expense-item').addEventListener('click', () => {
        addExpenseItem(categoryDiv, '', '');
    });
    
    categoryDiv.querySelector('.remove-category').addEventListener('click', () => categoryDiv.remove());
    
    // Add items if provided
    if (items && items.length) {
        items.forEach(item => {
            addExpenseItem(categoryDiv, item.name, item.amount);
        });
    } else {
        // Add at least one empty item
        addExpenseItem(categoryDiv, '', '');
    }
}

// Helper function to add expense item with data
function addExpenseItem(categoryDiv, name, amount) {
    const itemsDiv = categoryDiv.querySelector('.expense-items');
    const itemDiv = document.createElement('div');
    itemDiv.classList.add('row', 'g-2', 'expense-item', 'mb-2');
    
    // Ensure name is a string
    const itemName = typeof name === 'string' ? name : '';
    // Ensure amount is a number or can be parsed as a number
    const itemAmount = (typeof amount === 'number' || (typeof amount === 'string' && !isNaN(parseFloat(amount)))) 
                      ? amount : '';
                      
    itemDiv.innerHTML = `
        <div class="col-md-6">
            <input type="text" class="form-control" placeholder="Item Name" value="${itemName}" required>
        </div>
        <div class="col-md-4">
            <input type="number" class="form-control" placeholder="Amount" value="${itemAmount}" required>
        </div>
        <div class="col-md-2 d-grid">
            <button type="button" class="btn btn-danger remove-item">Remove</button>
        </div>
    `;
    itemsDiv.appendChild(itemDiv);
    itemDiv.querySelector('.remove-item').addEventListener('click', () => itemDiv.remove());
}

// Add income source
document.getElementById('add-income').addEventListener('click', () => {
    addIncomeItem('', '');
});

// Expense category options
const expenseCategoryOptions = [
    'Housing',
    'Utilities',
    'Groceries',
    'Transportation',
    'Healthcare',
    'Insurance',
    'Education',
    'Savings',
    'Debt Payments',
    'Personal Care',
    'Entertainment',
    'Dining Out',
    'Clothing',
    'Gifts & Donations',
    'Travel',
    'Childcare',
    'Pets',
    'Other'
];

// Add expense category (dropdown version)
document.getElementById('add-expense-category').addEventListener('click', () => {
    addExpenseCategory('', []);
});

// Save budget button
document.getElementById('save-budget').addEventListener('click', saveBudget);

async function saveBudget() {
    const budgetData = collectFormData();
    if (!budgetData.expenses || budgetData.expenses.length === 0) {
        alert('Please add at least one expense category before saving the budget.');
        return;
    }
    try {
        const res = await fetch('/save_budget', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(budgetData)
        });
        const data = await res.json();
        if (!res.ok || !data.success) {
            throw new Error(data.message || 'Failed to save budget');
        }
        alert('Budget saved successfully!');
        // Reload the page to show the updated budget list
        window.location.reload();
    } catch (error) {
        alert('Error: Could not save budget.');
        console.error('Save Budget Error:', error);
    }
}

// Collect form data
function collectFormData() {
    const budgetName = document.getElementById('budget-name').value;
    const currency = document.getElementById('currency').value;
    
    const income = Array.from(document.querySelectorAll('.income-item')).map(item => {
        const sourceInput = item.querySelector('input[type="text"]');
        const amountInput = item.querySelector('input[type="number"]');
        return {
            source: sourceInput ? sourceInput.value.trim() : '',
            amount: amountInput ? parseFloat(amountInput.value) : 0
        };
    }).filter(item => item.source && !isNaN(item.amount));
    
    const expenses = Array.from(document.querySelectorAll('.expense-category')).map(category => {
        const categorySelect = category.querySelector('.expense-category-select');
        // Ensure we have a valid category name
        let categoryName = 'Other';
        if (categorySelect && categorySelect.value && expenseCategoryOptions.includes(categorySelect.value)) {
            categoryName = categorySelect.value;
        }
        
        const items = Array.from(category.querySelectorAll('.expense-item')).map(item => {
            const nameInput = item.querySelector('input[type="text"]');
            const amountInput = item.querySelector('input[type="number"]');
            return {
                name: nameInput ? nameInput.value.trim() : '',
                amount: amountInput ? parseFloat(amountInput.value) : 0
            };
        }).filter(item => item.name && !isNaN(item.amount));
        
        return {
            category: categoryName,
            items: items
        };
    }).filter(cat => cat.items.length > 0);
    
    return { budgetName, currency, income, expenses };
}

// Clear form data function
function clearFormData() {
    // Clear existing income items (keep only the first one and reset its values)
    const incomeList = document.getElementById('income-list');
    while (incomeList.children.length > 1) {
        incomeList.removeChild(incomeList.lastChild);
    }
    
    // Reset the first income item
    if (incomeList.children.length > 0) {
        const firstIncomeItem = incomeList.children[0];
        const sourceInput = firstIncomeItem.querySelector('input[type="text"]');
        const amountInput = firstIncomeItem.querySelector('input[type="number"]');
        
        if (sourceInput) sourceInput.value = '';
        if (amountInput) amountInput.value = '';
    }
    
    // Clear all expense categories
    const expenseList = document.getElementById('expense-list');
    expenseList.innerHTML = '';
}
