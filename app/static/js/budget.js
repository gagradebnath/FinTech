// Budget page dynamic JS

// Load saved budget when clicking the load button
document.addEventListener('DOMContentLoaded', function() {
    const loadBudgetBtn = document.getElementById('load-budget');
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
