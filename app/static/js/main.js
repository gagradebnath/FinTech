// Main JavaScript for FinGuard app
console.log('FinGuard JS loaded');

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

// Example usage:
logToConsoleAndServer('JS loaded and logging enabled.');
