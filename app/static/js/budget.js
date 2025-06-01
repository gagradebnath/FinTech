// Budget page dynamic JS
// ...reference code from user prompt, adapted for relative Flask URLs and session-based auth...

// Add income source
document.getElementById('add-income').addEventListener('click', () => {
    const incomeList = document.getElementById('income-list');
    const div = document.createElement('div');
    div.classList.add('row', 'g-2', 'income-item', 'mb-2');
    div.innerHTML = `
        <div class="col-md-6">
            <input type="text" class="form-control" placeholder="Income Source" required>
        </div>
        <div class="col-md-4">
            <input type="number" class="form-control" placeholder="Amount" required>
        </div>
        <div class="col-md-2 d-grid">
            <button type="button" class="btn btn-danger remove-item">Remove</button>
        </div>
    `;
    incomeList.appendChild(div);
    div.querySelector('.remove-item').addEventListener('click', () => div.remove());
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
    const expenseList = document.getElementById('expense-list');
    const categoryDiv = document.createElement('div');
    categoryDiv.classList.add('expense-category', 'border', 'p-3', 'mb-3');
    categoryDiv.innerHTML = `
        <div class="mb-2">
            <select class="form-select expense-category-select" required>
                <option value="" disabled selected>Select Expense Category</option>
                ${expenseCategoryOptions.map(opt => `<option value="${opt}">${opt}</option>`).join('')}
            </select>
        </div>
        <div class="expense-items"></div>
        <button type="button" class="btn btn-sm btn-outline-success add-expense-item">+ Add Item</button>
        <button type="button" class="btn btn-sm btn-outline-danger remove-category">Remove Category</button>
    `;
    expenseList.appendChild(categoryDiv);
    categoryDiv.querySelector('.add-expense-item').addEventListener('click', () => {
        const itemsDiv = categoryDiv.querySelector('.expense-items');
        const itemDiv = document.createElement('div');
        itemDiv.classList.add('row', 'g-2', 'expense-item', 'mb-2');
        itemDiv.innerHTML = `
            <div class="col-md-6">
                <input type="text" class="form-control" placeholder="Item Name" required>
            </div>
            <div class="col-md-4">
                <input type="number" class="form-control" placeholder="Amount" required>
            </div>
            <div class="col-md-2 d-grid">
                <button type="button" class="btn btn-danger remove-item">Remove</button>
            </div>
        `;
        itemsDiv.appendChild(itemDiv);
        itemDiv.querySelector('.remove-item').addEventListener('click', () => itemDiv.remove());
    });
    categoryDiv.querySelector('.remove-category').addEventListener('click', () => categoryDiv.remove());
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
    } catch (error) {
        alert('Error: Could not save budget.');
        console.error('Save Budget Error:', error);
    }
}

// Collect form data
function collectFormData() {
    const budgetName = document.getElementById('budget-name').value;
    const currency = document.getElementById('currency').value;
    const income = Array.from(document.querySelectorAll('.income-item')).map(item => ({
        source: item.querySelector('input[type="text"]').value,
        amount: parseFloat(item.querySelector('input[type="number"]').value)
    }));
    const expenses = Array.from(document.querySelectorAll('.expense-category')).map(category => ({
        category: category.querySelector('input[type="text"]').value,
        items: Array.from(category.querySelectorAll('.expense-item')).map(item => ({
            name: item.querySelector('input[type="text"]').value,
            amount: parseFloat(item.querySelector('input[type="number"]').value)
        }))
    }));
    return { budgetName, currency, income, expenses };
}
