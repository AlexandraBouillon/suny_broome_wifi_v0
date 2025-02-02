let strobeAcknowledged = false;

function sendMessage() {
    const userInput = document.getElementById('userInput');
    const chatContainer = document.getElementById('chatContainer');
    const message = userInput.value.trim();

    if (!message) return;

    appendMessage('user-message', message);
    userInput.value = '';

    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({text: message})
    })
    .then(response => response.json())
    .then(data => appendMessage('assistant-message', data.reply))
    .catch(error => {
        console.error('Error:', error);
        appendMessage('assistant-message error', `Error: ${error.message || error}`);
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
    document.getElementById('userInput').addEventListener('keypress', e => {
        if (e.key === 'Enter') sendMessage();
    });

    document.getElementById('ledToggle').addEventListener('change', function() {
        window.location.href = this.checked ? '/light_on' : '/light_off';
    });
}); 