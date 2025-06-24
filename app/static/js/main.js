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
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'],                datasets: [{
                    label: 'Transactions',
                    data: [250, 300, 750, 400, 450, 460, 470, 480, 490],
                    backgroundColor: '#3ed6c2',
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
                            color: 'rgba(255, 255, 255, 0.05)'
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                },                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 26, 46, 0.9)',
                        titleColor: '#3ed6c2',
                        bodyColor: 'rgba(255, 255, 255, 0.8)',
                        borderColor: 'rgba(62, 214, 194, 0.3)',
                        borderWidth: 1
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
                    data: [30, 20, 35, 15],                    backgroundColor: [
                        '#ff6384',
                        '#3ed6c2',
                        '#ffcd56',
                        '#8a5fff'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(26, 26, 46, 0.9)',
                        titleColor: '#3ed6c2',
                        bodyColor: 'rgba(255, 255, 255, 0.8)',
                        borderColor: 'rgba(62, 214, 194, 0.3)',
                        borderWidth: 1
                    }
                },
                cutout: '70%'
            }
        });
    }
}

// Apply animations to elements
function applyAnimations() {
    document.querySelectorAll('.btn-outline-primary').forEach(btn => {
        btn.classList.add('btn-glow');
    });
}

// Initialize animations
document.addEventListener('DOMContentLoaded', function() {
    // Wait a short time for the DOM to fully render
    setTimeout(applyAnimations, 100);
});

// Set the active sidebar link based on current URL
function setActiveSidebarLink() {
    const currentUrl = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(link => {
        if (link.getAttribute('href') === currentUrl) {
            link.classList.add('active');
        }
    });
}
