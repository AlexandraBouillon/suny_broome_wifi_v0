// Debug logging helper
function log(message, error = false) {
    const style = error ? 'color: red; font-weight: bold;' : 'color: green;';
    console.log(`%c[PIXI Debug] ${message}`, style);
}

// LED configuration
const LED_CONFIG = {
    count: 50,
    baseSize: 20,
    sizeVariation: 15,
    colors: {
        blue: 0x3498db,
        red: 0xe74c3c,
        green: 0x2ecc71,
        gold: 0xedb31f
    },
    strobeColors: [0xFFFFFF, 0x000000],
    strobeSpeed: 100,
    animationSpeed: 0.06,
    statusCheckInterval: 500,
    glowIntensity: 25
};
// State tracking
let currentStatus = '';
let lastStatusCheck = 0;
let isStrobing = false;
let strobeInterval;
let strobeIndex = 0;
let time = 0;

function handleFlash() {
    // Show warning dialog first
    if (confirm("⚠️ WARNING: This animation contains flashing lights that may trigger seizures in people with photosensitive epilepsy.")) {
        log('Flash button clicked - warning accepted');
        fetch('/flash')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const statusElement = document.querySelector('.status');
                if (statusElement) {
                    statusElement.textContent = 'LED Status: FLASH';
                    currentStatus = 'FLASH';
                    log('Status updated to FLASH');
                }
            })
            .catch(error => {
                log(`Error in flash handler: ${error}`, true);
            });
    } else {
        log('Flash cancelled - warning declined');
    }
    return false;
}

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', async function() {
    log('DOM Content Loaded');

    // Check PIXI
    if (typeof PIXI === 'undefined') {
        log('PIXI is not loaded!', true);
        return;
    }
    log(`PIXI Version: ${PIXI.VERSION}`);

    // Check container
    const container = document.getElementById('pixiContainer');
    if (!container) {
        log('Container not found!', true);
        return;
    }
    log('Container found');

    try {
        // Create app
        const app = new PIXI.Application();
        log('Application created');

        // Initialize renderer
        await app.init({
            width: window.innerWidth,
            height: window.innerHeight,
            backgroundColor: 0x000000,
            resolution: window.devicePixelRatio || 1,
            antialias: true
        });
        log('Renderer initialized');

        // Add canvas to container
        container.appendChild(app.view);
        log('Canvas added to container');

        // Create LED array
        const leds = [];
        for (let i = 0; i < LED_CONFIG.count; i++) {
            const led = new PIXI.Graphics();
            const size = LED_CONFIG.baseSize + Math.random() * LED_CONFIG.sizeVariation;
            
            led.beginFill(0xedb31f);
            led.drawCircle(0, 0, size);
            led.endFill();
            
            led.x = Math.random() * app.screen.width;
            led.y = Math.random() * app.screen.height;
            
            const blurFilter = new PIXI.BlurFilter();
            blurFilter.blur = 15;
            blurFilter.quality = 1;
            led.filters = [blurFilter];
            
            app.stage.addChild(led);
            leds.push({
                graphic: led,
                filter: blurFilter,
                speed: 0.8 + Math.random() * 0.7,
                phase: Math.random() * Math.PI * 2,
                velocityX: (Math.random() - 0.5) * 2,
                velocityY: (Math.random() - 0.5) * 2
            });
        }
        log('LEDs created');

        // Color cycle function
       
function cycleLEDColors(led, index, time) {
    // Ensure color values stay within valid range (0-255)
    const r = Math.min(255, Math.floor(Math.sin(time + led.phase) * 127 + 178));
    const g = Math.min(255, Math.floor(Math.sin(time + led.phase + 2) * 127 + 178));
    const b = Math.min(255, Math.floor(Math.sin(time + led.phase + 4) * 127 + 178));
    
    // Convert to hex color
    const color = (r << 16) | (g << 8) | b;
    
    led.graphic.clear();
    led.graphic.beginFill(color);
    led.graphic.drawCircle(0, 0, LED_CONFIG.baseSize);
    led.graphic.endFill();
    
    // Update glow effect
    led.filter.blur = LED_CONFIG.glowIntensity + Math.sin(time) * 8;
}

        function startStrobe() {
            if (isStrobing) return;
            
            log('Starting strobe effect');
            isStrobing = true;
            strobeIndex = 0;
            
            strobeInterval = setInterval(() => {
                const color = LED_CONFIG.strobeColors[strobeIndex % 2];
                leds.forEach(led => {
                    led.graphic.clear();
                    led.graphic.beginFill(color);
                    led.graphic.drawCircle(0, 0, LED_CONFIG.baseSize);
                    led.graphic.endFill();
                    led.graphic.alpha = 1;
                });
                log(`Strobe pulse: ${strobeIndex % 2 ? 'OFF' : 'ON'}`);
                strobeIndex++;
            }, LED_CONFIG.strobeSpeed);
        }

        function stopStrobe() {
            if (!isStrobing) return;
            
            log('Stopping strobe effect');
            isStrobing = false;
            clearInterval(strobeInterval);
            
            leds.forEach(led => {
                led.graphic.scale.set(1);
                led.filter.blur = 15;
            });
        }

        // Main animation loop with throttled status checking
        app.ticker.add(() => {
            const now = Date.now();
            
            if (now - lastStatusCheck >= LED_CONFIG.statusCheckInterval) {
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

            // Update animation based on current status
            if (currentStatus.includes('FLASH')) {
                // Strobe effect is handled by interval
            } else if (currentStatus.includes('ON')) {
                time += LED_CONFIG.animationSpeed;
                leds.forEach((led, index) => {
                    cycleLEDColors(led, index, time * led.speed);
                    updateLEDPosition(led, app.screen.width, app.screen.height);
                    led.graphic.alpha = 1;
                });
            } else {
                // OFF state
                leds.forEach(led => {
                    led.graphic.alpha = 0;
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

        log('Animation initialized successfully');

    } catch (error) {
        log(`Initialization error: ${error.message}`, true);
        console.error(error);
    }
});

// Helper function to update LED position
function updateLEDPosition(led, width, height) {
    try {
        led.graphic.x += led.velocityX * 1.5;
        led.graphic.y += led.velocityY * 1.5;
        
        led.graphic.x += Math.sin(time * led.speed) * 3;
        led.graphic.y += Math.cos(time * led.speed) * 3;
        
        // Boundary checking
        if (led.graphic.x < 0) led.graphic.x = 0;
        if (led.graphic.x > width) led.graphic.x = width;
        if (led.graphic.y < 0) led.graphic.y = 0;
        if (led.graphic.y > height) led.graphic.y = height;
        
        if (led.graphic.x <= 0 || led.graphic.x >= width) {
            led.velocityX *= -1;
        }
        if (led.graphic.y <= 0 || led.graphic.y >= height) {
            led.velocityY *= -1;
        }
    } catch (error) {
        log(`Error updating LED position: ${error.message}`, true);
    }
}