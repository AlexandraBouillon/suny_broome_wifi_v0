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

    userInput.addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    ledToggle.addEventListener('change', () => {
        window.location.href = ledToggle.checked ? '/light_on' : '/light_off';
    });
}); 