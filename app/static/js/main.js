// Main JavaScript for FinGuard app
console.log('FinGuard JS loaded');

// Logging function
function logToConsoleAndServer(message) {
    // Log to browser console
    console.log('[FinGuard]', message);
    // Log to server (terminal) via fetch
    fetch('/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
    });
}

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('collapsed');
            document.querySelector('.content').classList.toggle('expanded');
        });
    }

    // Initialize any charts
    initializeCharts();

    // Set active sidebar link based on current URL
    setActiveSidebarLink();
    
    // Example usage of logging
    logToConsoleAndServer('Dashboard JS initialized');
});

// Initialize charts if they exist on the page
function initializeCharts() {
    // Transaction chart
    const txChartEl = document.getElementById('transactionChart');
    if (txChartEl) {
        new Chart(txChartEl, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],
                datasets: [{
                    label: 'Transactions',
                    data: [250, 300, 750, 400, 450, 460, 470, 480, 490],
                    backgroundColor: '#0066ff',
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }

    // Expense chart
    const expenseChartEl = document.getElementById('expenseChart');
    if (expenseChartEl) {
        new Chart(expenseChartEl, {
            type: 'doughnut',
            data: {
                labels: ['Shopping', 'Food', 'Travel', 'Health'],
                datasets: [{
                    data: [30, 20, 35, 15],
                    backgroundColor: [
                        '#ff6384',
                        '#36a2eb',
                        '#ffcd56',
                        '#4bc0c0'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                cutout: '70%'
            }
        });
    }
}

// Set the active sidebar link based on current URL
function setActiveSidebarLink() {
    const currentUrl = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
        if (link.getAttribute('href') === currentUrl) {
            link.classList.add('active');
        }
    });
}
