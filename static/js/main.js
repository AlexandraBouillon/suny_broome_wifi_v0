document.addEventListener('DOMContentLoaded', function() {
    const ledToggle = document.getElementById('ledToggle');
    const statusDiv = document.querySelector('.status');
    const animationContainer = document.getElementById('pixiContainer');
    const chatContainer = document.getElementById('chatContainer');
    const userInput = document.getElementById('userInput');

    // Initialize states
    let isAnimating = false;
    let flashTimeout = null;
    let strobeAcknowledged = false;

    // LED Toggle functionality
    ledToggle.addEventListener('change', function() {
        const url = this.checked ? '/light_on' : '/light_off';
        fetch(url)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                toggleAnimation(this.checked);
            })
            .catch(error => {
                console.error('Error:', error);
                this.checked = !this.checked; // Revert toggle if request failed
            });
    });

    // Animation functions
    function toggleAnimation(isOn) {
        isAnimating = isOn;
        if (isOn) {
            startAnimation();
        } else {
            stopAnimation();
        }
    }

    // Chat functionality
    function addMessage(message, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = isUser ? 'user-message' : 'ai-message';
        messageDiv.textContent = message;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    window.sendMessage = function() {
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, true);
        userInput.value = '';

        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: message })
        })
        .then(response => response.json())
        .then(data => {
            addMessage(data.reply);
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('Sorry, I encountered an error processing your request.');
        });
    };

    // Strobe warning functionality
    window.confirmStrobe = function() {
        if (!strobeAcknowledged) {
            document.getElementById('strobeWarning').style.display = 'flex';
            return false;
        }
        return true;
    };

    window.acknowledgeWarning = function() {
        strobeAcknowledged = true;
        document.getElementById('strobeWarning').style.display = 'none';
        handleFlash();
    };

    // Flash button functionality
    window.handleFlash = function() {
        if (!confirmStrobe()) return;

        fetch('/flash')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                executeFlashAnimation();
            })
            .catch(error => console.error('Error:', error));
    };

    function executeFlashAnimation() {
        if (flashTimeout) {
            clearTimeout(flashTimeout);
        }
        
        const originalState = ledToggle.checked;
        ledToggle.checked = false;
        toggleAnimation(false);
        
        flashTimeout = setTimeout(() => {
            ledToggle.checked = originalState;
            toggleAnimation(originalState);
            flashTimeout = null;
        }, 500);
    }

    // Event listeners
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            window.sendMessage();
        }
    });

    // Initialize state based on server status
    const currentStatus = statusDiv.textContent.includes('ON');
    ledToggle.checked = currentStatus;
    toggleAnimation(currentStatus);
}); 