let strobeAcknowledged = false;

function sendMessage() {
    const userInput = document.getElementById('userInput');
    const message = userInput.value.trim();

    if (!message) return;

    appendMessage('user-message', message);
    userInput.value = '';

    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: message })
    })
        .then(response => {
            if (!response.ok) throw new Error('Network response failed');
            return response.json();
        })
        .then(data => appendMessage('assistant-message', data.reply))
        .catch(error => {
            console.error('Error:', error);
            appendMessage('assistant-message error', `Error: ${error.message}`);
        });
}

function appendMessage(className, text) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.textContent = text;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function confirmStrobe() {
    if (!strobeAcknowledged) {
        document.getElementById('strobeWarning').style.display = 'flex';
        return false;
    }
    return true;
}

function acknowledgeWarning() {
    strobeAcknowledged = true;
    document.getElementById('strobeWarning').style.display = 'none';
    document.querySelector('.flash-button').click();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    const userInput = document.getElementById('userInput');
    const ledToggle = document.getElementById('ledToggle');
    const statusElement = document.querySelector('.status');

    // Set initial toggle state based on LED status
    if (statusElement) {
        const currentStatus = statusElement.textContent;
        ledToggle.checked = currentStatus.includes('ON');
    }

    userInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    ledToggle.addEventListener('click', async (e) => {
        // Prevent the default checkbox behavior
        e.preventDefault();
        
        // Toggle the checked state manually
        ledToggle.checked = !ledToggle.checked;
        
        // Store the new state
        const newState = ledToggle.checked;
        console.log('Toggle clicked, new state:', newState);
        
        try {
            const endpoint = newState ? '/light_on' : '/light_off';
            console.log('Sending request to:', endpoint);
            
            const response = await fetch(endpoint);
            
            if (!response.ok) {
                throw new Error('Failed to toggle LED');
            }
            
            // Update the status text immediately
            if (statusElement) {
                statusElement.textContent = `LED Status: ${newState ? 'ON' : 'OFF'}`;
                console.log('Status updated to:', statusElement.textContent);
            }
            
            // Reload page after a short delay to allow animation to complete
            setTimeout(() => {
                window.location.reload();
            }, 400);
            
        } catch (error) {
            console.error('Error:', error);
            // Revert toggle state on error
            ledToggle.checked = !newState;
            if (statusElement) {
                statusElement.textContent = `LED Status: ${!newState ? 'ON' : 'OFF'}`;
            }
        }
    });
}); 