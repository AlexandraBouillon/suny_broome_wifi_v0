// Debug logging helper
function log(message, error = false) {
    const style = error ? 'color: red; font-weight: bold;' : 'color: green;';
    console.log(`%c[PIXI Debug] ${message}`, style);
}

// Improved LED configuration with better organization
const LED_CONFIG = {
    count: 50,
    appearance: {
        baseSize: 20,
        sizeVariation: 15,
        glowIntensity: 35,
        blurQuality: 1,
        blurAmount: 15,
        brightness: {
            on: 1.0,
            off: 0.0,
            strobe: 1.0
        }
    },
    colors: {
        blue: 0x3498db,
        red: 0xe74c3c,
        green: 0x2ecc71,
        gold: 0xedb31f,
        strobe: [0xedb31f, 0x000000]  // Using gold color for strobe
    },
    animation: {
        speed: 0.06,
        statusCheckInterval: 500,
        strobeSpeed: 100,     // 100ms for strobe interval
        flashDuration: 10000  // 10 seconds
    }
};

// State tracking
let currentStatus = '';
let lastStatusCheck = 0;
let isStrobing = false;
let strobeInterval;
let strobeIndex = 0;
let time = 0;
let app = null;
let animationStarted = false;
let leds = [];

// Global animation control functions
window.startAnimation = function() {
    if (!app) return;
    log('Starting animation');
    animationStarted = true;
    currentStatus = 'ON';
    
    // Show and animate LEDs
    leds.forEach(led => {
        led.graphic.alpha = LED_CONFIG.appearance.brightness.on;
        led.filter.blur = LED_CONFIG.appearance.glowIntensity;
    });
}

window.stopAnimation = function() {
    if (!app) return;
    log('Stopping animation');
    animationStarted = false;
    currentStatus = 'OFF';
    if (isStrobing) stopStrobe();
    
    // Hide all LEDs
    leds.forEach(led => {
        led.graphic.alpha = 0;
    });
}

function handleFlash() {
    if (confirm("⚠️ WARNING: This animation contains flashing lights that may trigger seizures in people with photosensitive epilepsy.")) {
        log('Flash button clicked - warning accepted');
        
        const statusElement = document.querySelector('.status');
        if (statusElement) {
            statusElement.textContent = 'LED Status: FLASH';
            currentStatus = 'FLASH';
            log('Status updated to FLASH');
            startStrobe();  // Start strobe immediately after status update
        }

        fetch('/flash')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
            })
            .catch(error => {
                log(`Error in flash handler: ${error}`, true);
                stopStrobe();
                if (statusElement) {
                    statusElement.textContent = 'LED Status: OFF';
                    currentStatus = 'OFF';
                }
            });
    } else {
        log('Flash cancelled - warning declined');
    }
    return false;
}

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', async function() {
    log('DOM Content Loaded');

    if (typeof PIXI === 'undefined') {
        log('PIXI is not loaded!', true);
        return;
    }
    log(`PIXI Version: ${PIXI.VERSION}`);

    const container = document.getElementById('pixiContainer');
    if (!container) {
        log('Container not found!', true);
        return;
    }
    log('Container found');

    try {
        // Create and initialize PIXI application
        app = new PIXI.Application();
        log('Application created');

        await app.init({
            width: window.innerWidth,
            height: window.innerHeight,
            backgroundColor: 0x000000,
            resolution: window.devicePixelRatio || 1,
            antialias: true,
            backgroundAlpha: 1
        });

        container.appendChild(app.view);
        log('Canvas added to container');

        // Initialize in OFF state
        const statusElement = document.querySelector('.status');
        if (statusElement) {
            statusElement.textContent = 'LED Status: OFF';
            currentStatus = 'OFF';
        }

        const ledToggle = document.getElementById('ledToggle');
        if (ledToggle) {
            ledToggle.checked = false;
        }

        // Create LED array
        leds = [];
        for (let i = 0; i < LED_CONFIG.count; i++) {
            const led = createLED(app);
            if (led && led.graphic) {
                app.stage.addChild(led.graphic);
                leds.push(led);
                led.graphic.alpha = 0; // Start with invisible LEDs
            }
        }
        log(`Created ${leds.length} LEDs successfully`);

        // Animation loop
        app.ticker.add(() => {
            if (!animationStarted && !isStrobing) {
                // Ensure background is black and LEDs are invisible
                app.renderer.background.color = 0x000000;
                leds.forEach(led => {
                    led.graphic.alpha = 0;
                });
                return;
            }

            const now = Date.now();

            if (now - lastStatusCheck >= LED_CONFIG.animation.statusCheckInterval) {
                const statusElement = document.querySelector('.status');
                if (statusElement) {
                    const newStatus = statusElement.textContent.trim();
                    if (newStatus !== currentStatus) {
                        log('Status changed to: ' + newStatus);
                        currentStatus = newStatus;
                        if (newStatus.includes('FLASH')) {
                            if (!isStrobing) startStrobe();
                        } else {
                            if (isStrobing) stopStrobe();
                        }
                    }
                }
                lastStatusCheck = now;
            }

            if (currentStatus.includes('ON') && animationStarted) {
                time += LED_CONFIG.animation.speed;
                leds.forEach(led => {
                    cycleLEDColors(led, time * led.speed);
                    updateLEDPosition(led, app.screen.width, app.screen.height);
                });
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            app.renderer.resize(window.innerWidth, window.innerHeight);
            leds.forEach(led => {
                led.graphic.x = Math.random() * app.screen.width;
                led.graphic.y = Math.random() * app.screen.height;
            });
        });

        // Handle visibility change
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                app.stop();
                stopStrobe();
            } else {
                app.start();
            }
        });

        animationStarted = false;
        log('Animation initialized successfully in OFF state');

        // Add flash complete listener
        document.addEventListener('flashComplete', function(e) {
            log('Flash complete event received');
            stopStrobe();
            updateStatus('OFF');
            stopAnimation();
        });

        function updateStatus(status) {
            const statusDiv = document.querySelector('.status');
            if (statusDiv) {
                statusDiv.textContent = `LED Status: ${status}`;
                log(`Status changed to: LED Status: ${status}`);
            }
        }

    } catch (error) {
        log(`Initialization error: ${error.message}`, true);
        console.error(error);
    }
});

// Your existing helper functions remain unchanged
function updateLEDPosition(led, width, height) {
    // ... existing function ...
}

function createLED(app) {
    try {
        const size = LED_CONFIG.appearance.baseSize + Math.random() * LED_CONFIG.appearance.sizeVariation;
        const led = new PIXI.Graphics();
        
        led.beginFill(LED_CONFIG.colors.gold);
        led.drawCircle(0, 0, size);
        led.endFill();
        
        led.x = Math.random() * app.screen.width;
        led.y = Math.random() * app.screen.height;
        
        const blurFilter = new PIXI.BlurFilter();
        blurFilter.blur = LED_CONFIG.appearance.blurAmount;
        blurFilter.quality = LED_CONFIG.appearance.blurQuality;
        led.filters = [blurFilter];
        
        return {
            graphic: led,
            filter: blurFilter,
            speed: 0.8 + Math.random() * 0.7,
            phase: Math.random() * Math.PI * 2,
            velocityX: (Math.random() - 0.5) * 2,
            velocityY: (Math.random() - 0.5) * 2
        };
    } catch (error) {
        log(`Error creating LED: ${error.message}`, true);
        return null;
    }
}

function cycleLEDColors(led, time) {
    const r = Math.min(255, Math.floor(Math.sin(time + led.phase) * 127 + 178));
    const g = Math.min(255, Math.floor(Math.sin(time + led.phase + 2) * 127 + 178));
    const b = Math.min(255, Math.floor(Math.sin(time + led.phase + 4) * 127 + 178));
    const color = (r << 16) | (g << 8) | b;

    led.graphic.clear()
        .beginFill(color)
        .drawCircle(0, 0, LED_CONFIG.appearance.baseSize)
        .endFill();

    led.filter.blur = LED_CONFIG.appearance.glowIntensity + Math.sin(time) * 8;
}

function startStrobe() {
    if (isStrobing) return;
    log('Starting strobe effect');
    isStrobing = true;
    strobeIndex = 0;

    // Store original state
    const originalState = currentStatus;

    // Make sure animation is running
    animationStarted = true;

    strobeInterval = setInterval(() => {
        const isOn = strobeIndex % 2 === 0;
        leds.forEach(led => {
            led.graphic.clear();
            led.graphic.beginFill(LED_CONFIG.colors.gold);  // Always use gold
            led.graphic.drawCircle(0, 0, LED_CONFIG.appearance.baseSize);
            led.graphic.endFill();
            led.graphic.alpha = isOn ? 1 : 0;
            // Increase glow effect during strobe
            led.filter.blur = isOn ? LED_CONFIG.appearance.glowIntensity * 2.5 : 0;
        });
        strobeIndex++;
    }, LED_CONFIG.animation.strobeSpeed);

    // Stop strobe after duration
    setTimeout(() => {
        stopStrobe();
        // Return to previous state
        const statusElement = document.querySelector('.status');
        if (statusElement) {
            statusElement.textContent = `LED Status: ${originalState}`;
            currentStatus = originalState;
        }
        // Update toggle button and animation state
        const ledToggle = document.getElementById('ledToggle');
        if (ledToggle) {
            ledToggle.checked = originalState.includes('ON');
        }
        if (originalState.includes('ON')) {
            window.startAnimation();
        } else {
            window.stopAnimation();
        }
    }, LED_CONFIG.animation.flashDuration);
}

function stopStrobe() {
    if (!isStrobing) return;
    log('Stopping strobe effect');
    isStrobing = false;
    clearInterval(strobeInterval);
    strobeInterval = null;
} 