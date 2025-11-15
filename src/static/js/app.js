// Check API status on page load
async function checkStatus() {
    const statusBadge = document.getElementById('statusBadge');
    const statusText = document.getElementById('statusText');

    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        if (response.ok && data.status === 'ok') {
            statusBadge.classList.add('online');
            statusText.textContent = 'Online';
        } else {
            statusBadge.classList.add('offline');
            statusText.textContent = 'Offline';
        }
    } catch (error) {
        statusBadge.classList.add('offline');
        statusText.textContent = 'Error';
        console.error('Status check failed:', error);
    }
}

// Test endpoint function
async function testEndpoint(endpoint) {
    const responseArea = document.getElementById('responseArea');
    const responseContent = document.getElementById('responseContent');

    responseArea.style.display = 'block';
    responseContent.textContent = 'Loading...';

    try {
        const startTime = performance.now();
        const response = await fetch(endpoint);
        const endTime = performance.now();
        const data = await response.json();

        const responseData = {
            status: response.status,
            statusText: response.statusText,
            time: `${(endTime - startTime).toFixed(2)}ms`,
            data: data
        };

        responseContent.textContent = JSON.stringify(responseData, null, 2);
    } catch (error) {
        responseContent.textContent = JSON.stringify({
            error: error.message
        }, null, 2);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();

    // Refresh status every 30 seconds
    setInterval(checkStatus, 30000);
});

// Add smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
