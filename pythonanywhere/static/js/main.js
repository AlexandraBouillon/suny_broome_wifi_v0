document.addEventListener('DOMContentLoaded', function() {
    const ledToggle = document.getElementById('ledToggle');
    const statusDiv = document.querySelector('.status');
    const tempDiv = document.querySelector('.temperature');
    const animationContainer = document.getElementById('pixiContainer');
    const chatInput = document.getElementById('chatInput');
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');

    // Initialize animation state
    let isAnimating = false;
    let flashTimeout = null;
    let lastTemperature = null;
    let isCheckingTemperature = false;

    // Debug logging
    function debugLog(message) {
        console.log('[Debug]', message);
    }

    // Update temperature display
    function updateTemperatureDisplay(temperature) {
        if (tempDiv) {
            tempDiv.textContent = `Temperature: ${temperature}°C`;
            debugLog(`Temperature updated to: ${temperature}°C`);
        }
    }

    // Periodic temperature check
    async function checkTemperature() {
        if (isCheckingTemperature) return;
        isCheckingTemperature = true;
        
        try {
            debugLog('Checking temperature...');
            const ledToggle = document.getElementById('ledToggle');
            const statusDiv = document.querySelector('.status');
            let status = ledToggle && ledToggle.checked ? 'ON' : 'OFF';
            
            // Check if currently flashing
            if (statusDiv && statusDiv.textContent.includes('FLASH')) {
                status = 'FLASH';
            }
            
            debugLog(`Initial status: ${status}`);
            
            const response = await fetch(`/update_temperature?status=${status}`);
            const data = await response.json();
            
            if (data.success) {
                const newTemp = parseFloat(data.temperature);
                const prevTemp = parseFloat(data.previous_temperature);
                
                debugLog(`Previous temperature: ${prevTemp}°C`);
                debugLog(`New temperature: ${newTemp}°C`);
                
                if (newTemp !== prevTemp) {
                    debugLog(`Temperature updated to: ${newTemp}°C`);
                    debugLog(`Temperature changed from ${prevTemp}°C to ${newTemp}°C`);
                    lastTemperature = newTemp;
                    updateTemperatureDisplay(newTemp);
                } else {
                    debugLog('Temperature unchanged');
                }
            }
        } catch (error) {
            console.error('Error checking temperature:', error);
        } finally {
            isCheckingTemperature = false;
        }
    }

    // Check temperature every 2 seconds instead of 3
    const tempCheckInterval = setInterval(checkTemperature, 2000);

    // LED Toggle functionality
    if (ledToggle) {
        ledToggle.addEventListener('change', function() {
            debugLog(`Toggle changed to: ${this.checked}`);
            const url = this.checked ? '/light_on' : '/light_off';
            
            fetch(url)
                .then(response => {
                    if (!response.ok) throw new Error('Network response was not ok');
                    return response.json();
                })
                .then(data => {
                    debugLog('Updating animation state and temperature');
                    if (statusDiv) {
                        statusDiv.textContent = `LED Status: ${data.status}`;
                    }
                    if (data.temperature) {
                        updateTemperatureDisplay(data.temperature);
                    }
                    toggleAnimation(this.checked);
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.checked = !this.checked;
                    if (statusDiv) {
                        statusDiv.textContent = `LED Status: ${this.checked ? 'ON' : 'OFF'}`;
                    }
                });
        });
    }

    function toggleAnimation(isOn) {
        debugLog(`Toggling animation: ${isOn}`);
        if (isOn) {
            startAnimation();
        } else {
            stopAnimation();
        }
    }

    // Chat functionality
    if (chatForm && chatInput && chatMessages) {
        async function sendMessage(text) {
            try {
                debugLog(`Sending chat message: ${text}`);
                const payload = { text: text };
                debugLog(`Request payload: ${JSON.stringify(payload)}`);
                
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                debugLog(`Received response: ${JSON.stringify(data)}`);
                return data.reply;
            } catch (error) {
                console.error('Error:', error);
                throw error;
            }
        }

        function addMessage(text, isUser = false) {
            debugLog(`Adding message: ${text} (isUser: ${isUser})`);
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'message user-message' : 'message assistant-message';
            messageDiv.textContent = text;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            debugLog('Form submitted');
            
            const text = chatInput.value.trim();
            debugLog(`Input text: "${text}"`);
            
            if (!text) {
                debugLog('Empty input, ignoring');
                return;
            }

            addMessage(text, true);
            chatInput.value = '';

            try {
                const response = await sendMessage(text);
                debugLog(`Got response: ${response}`);
                addMessage(response);
            } catch (error) {
                console.error('Chat error:', error);
                addMessage('Sorry, I encountered an error processing your request.');
            }
        });
    } else {
        console.warn('Chat elements not found in the DOM');
    }

    // Initialize state based on server status
    if (statusDiv) {
        const currentStatus = statusDiv.textContent.includes('ON');
        debugLog(`Initial status: ${currentStatus}`);
        if (ledToggle) {
            ledToggle.checked = currentStatus;
        }
        toggleAnimation(currentStatus);
    }
}); 