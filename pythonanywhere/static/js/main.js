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

    // Add Chart.js to your HTML
    const chartScript = document.createElement('script');
    chartScript.src = 'https://cdn.jsdelivr.net/npm/chart.js';
    document.head.appendChild(chartScript);

    // ML Analysis Data Structure
    const mlAnalysis = {
        basicStatistics: {
            usage: {
                mean: 691841.40,
                std: 92422.15,
                min: 359062.00,
                max: 989800.00,
                median: 686517.50
            },
            cost: {
                mean: 51378.75,
                std: 15653.12,
                min: 5536.80,
                max: 103529.31,
                median: 52442.03,
                perKwh: 0.073728
            }
        },
        seasonalUsage: {
            Winter: { usage: 661428.74, peak: 1327.16, offPeak: 1074.45 },
            Spring: { usage: 627093.71, peak: 1457.04, offPeak: 1078.75 },
            Summer: { usage: 761196.80, peak: 1678.30, offPeak: 1248.49 },
            Fall: { usage: 717073.68, peak: 1577.28, offPeak: 1193.77 }
        },
        yearlyTrends: {
            '2020': { avgUsage: 680000, avgCost: 50000 },
            '2021': { avgUsage: 695000, avgCost: 52000 },
            '2022': { avgUsage: 705000, avgCost: 54000 },
            '2023': { avgUsage: 710000, avgCost: 56000 }
        },
        anomalies: {
            count: 28,
            significantEvents: [
                { date: '2020-05', usage: 359062, reason: 'Lowest usage month' },
                { date: '2003-09', usage: 989800, reason: 'Highest usage month' }
            ]
        },
        modelPerformance: {
            r2_training: 0.902,
            r2_testing: 0.369,
            mse: 146660924.52,
            featureImportance: {
                'Off-Peak': 0.400414,
                'Total Usage': 0.296431,
                'On-Peak': 0.214203,
                'Month_Sin': 0.046054,
                'Month_Cos': 0.042897
            }
        }
    };

    // Query Pattern Matcher
    const queryPatterns = {
        statistics: ['statistics', 'stats', 'numbers', 'figures', 'data'],
        seasonal: ['seasonal', 'season', 'winter', 'summer', 'spring', 'fall'],
        trends: ['trend', 'yearly', 'year over year', 'yoy', 'historical'],
        peaks: ['peak', 'demand', 'maximum', 'highest'],
        costs: ['cost', 'price', 'expense', 'bill', 'spending'],
        efficiency: ['efficiency', 'performance', 'optimization'],
        anomalies: ['anomaly', 'unusual', 'irregular', 'outlier'],
        comparison: ['compare', 'versus', 'vs', 'difference', 'between'],
        visualization: ['show', 'graph', 'chart', 'plot', 'visual']
    };

    // Debug function for visualization
    function debugVisualization(message) {
        console.log('[Visualization Debug]:', message);
    }

    // Get or create visualization container
    function getVisualizationContainer() {
        let container = document.getElementById('visualizationContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'visualizationContainer';
            container.className = 'visualization-container';
            if (chatMessages) {
                chatMessages.parentNode.insertBefore(container, chatMessages.nextSibling);
            }
            debugVisualization('Created new visualization container');
        }
        return container;
    }

    // If you need to debug the container, use the function:
    debugVisualization('Initial container state: ' + getVisualizationContainer());

    // Modified createChart function
    function createChart(type, data, labels, title) {
        try {
            const container = getVisualizationContainer();
            container.innerHTML = '';
            
            const canvas = document.createElement('canvas');
            container.appendChild(canvas);
            const ctx = canvas.getContext('2d');

            // Set initial canvas styles
            ctx.fillStyle = '#000000'; // Black background
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const chart = new Chart(canvas, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [{
                        label: title,
                        data: data,
                        backgroundColor: 'rgba(255, 215, 0, 0.6)',
                        borderColor: '#FFD700',
                        borderWidth: 2,
                        pointBackgroundColor: '#FFD700',
                        pointBorderColor: '#000000',
                        pointHoverBackgroundColor: '#FFD700',
                        pointHoverBorderColor: '#FFFFFF'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            labels: {
                                color: '#FFD700',
                                font: {
                                    size: 14,
                                    weight: 'bold',
                                    family: 'Arial'
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: title,
                            color: '#FFD700',
                            font: {
                                size: 16,
                                weight: 'bold',
                                family: 'Arial'
                            },
                            padding: 20
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                color: 'rgba(255, 215, 0, 0.2)',
                                borderColor: '#FFD700',
                                drawBorder: true,
                                drawOnChartArea: true
                            },
                            ticks: {
                                color: '#FFD700',
                                font: {
                                    size: 12,
                                    weight: 'bold'
                                }
                            },
                            afterDraw: (chart) => {
                                const ctx = chart.ctx;
                                ctx.save();
                                ctx.strokeStyle = '#FFD700';
                                ctx.lineWidth = 2;
                                // Draw x-axis line
                                ctx.beginPath();
                                ctx.moveTo(chart.chartArea.left, chart.chartArea.bottom);
                                ctx.lineTo(chart.chartArea.right, chart.chartArea.bottom);
                                ctx.stroke();
                                ctx.restore();
                            }
                        },
                        y: {
                            grid: {
                                color: 'rgba(255, 215, 0, 0.2)',
                                borderColor: '#FFD700',
                                drawBorder: true,
                                drawOnChartArea: true
                            },
                            ticks: {
                                color: '#FFD700',
                                font: {
                                    size: 12,
                                    weight: 'bold'
                                }
                            },
                            afterDraw: (chart) => {
                                const ctx = chart.ctx;
                                ctx.save();
                                ctx.strokeStyle = '#FFD700';
                                ctx.lineWidth = 2;
                                // Draw y-axis line
                                ctx.beginPath();
                                ctx.moveTo(chart.chartArea.left, chart.chartArea.top);
                                ctx.lineTo(chart.chartArea.left, chart.chartArea.bottom);
                                ctx.stroke();
                                ctx.restore();
                            }
                        }
                    },
                    animation: {
                        onComplete: function(animation) {
                            const ctx = this.ctx;
                            ctx.save();
                            // Redraw text elements to ensure visibility
                            ctx.fillStyle = '#FFD700';
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            // Additional text rendering if needed
                            ctx.restore();
                        }
                    }
                }
            });

            return chart;
        } catch (error) {
            console.error('Error creating chart:', error);
            const container = getVisualizationContainer();
            container.innerHTML = `<p class="error">Error creating visualization: ${error.message}</p>`;
        }
    }

    // Enhanced Analysis Functions
    function analyzeQuery(text) {
        const lowerText = text.toLowerCase();
        let matchedPatterns = [];

        for (const [pattern, keywords] of Object.entries(queryPatterns)) {
            if (keywords.some(keyword => lowerText.includes(keyword))) {
                matchedPatterns.push(pattern);
            }
        }

        return matchedPatterns;
    }

    function generateComparison(aspect1, aspect2) {
        let response = '';
        
        if (aspect1 in mlAnalysis.seasonalUsage && aspect2 in mlAnalysis.seasonalUsage) {
            const diff = mlAnalysis.seasonalUsage[aspect1].usage - mlAnalysis.seasonalUsage[aspect2].usage;
            response = `Comparing ${aspect1} vs ${aspect2}:\n` +
                      `${aspect1}: ${mlAnalysis.seasonalUsage[aspect1].usage.toFixed(2)} kWh\n` +
                      `${aspect2}: ${mlAnalysis.seasonalUsage[aspect2].usage.toFixed(2)} kWh\n` +
                      `Difference: ${diff.toFixed(2)} kWh (${((diff/mlAnalysis.seasonalUsage[aspect2].usage)*100).toFixed(1)}%)`;
        }

        return response;
    }

    // Modified formatResponse function with explicit visualization handling
    function formatResponse(patterns, text) {
        let response = '';
        let visualizationData = null;

        // Debug logging
        console.log('Formatting response for patterns:', patterns);
        console.log('Text:', text);

        if (patterns.includes('visualization') || text.toLowerCase().includes('show') || 
            text.toLowerCase().includes('usage') || text.toLowerCase().includes('graph')) {
            console.log('Visualization requested');
            
            if (patterns.includes('seasonal') || text.toLowerCase().includes('season')) {
                visualizationData = {
                    type: 'bar',
                    labels: Object.keys(mlAnalysis.seasonalUsage),
                    data: Object.values(mlAnalysis.seasonalUsage).map(s => s.usage),
                    title: 'Seasonal Usage Analysis'
                };
            } else if (patterns.includes('trends') || text.toLowerCase().includes('trend')) {
                visualizationData = {
                    type: 'line',
                    labels: Object.keys(mlAnalysis.yearlyTrends),
                    data: Object.values(mlAnalysis.yearlyTrends).map(y => y.avgUsage),
                    title: 'Yearly Usage Trends'
                };
            } else {
                // Default visualization if no specific type is requested
                visualizationData = {
                    type: 'bar',
                    labels: Object.keys(mlAnalysis.seasonalUsage),
                    data: Object.values(mlAnalysis.seasonalUsage).map(s => s.usage),
                    title: 'Energy Usage Analysis'
                };
            }

            console.log('Visualization data:', visualizationData);
            
            if (visualizationData) {
                const vizContainer = document.getElementById('visualizationContainer');
                if (vizContainer) {
                    console.log('Creating chart...');
                    createChart(
                        visualizationData.type,
                        visualizationData.data,
                        visualizationData.labels,
                        visualizationData.title
                    );
                    response += 'I\'ve created a visualization based on your request. You can see it below.\n';
                } else {
                    console.error('Visualization container not found');
                    response += 'Sorry, I couldn\'t create the visualization due to a technical error.\n';
                }
            }
        }

        if (patterns.includes('comparison')) {
            const seasons = ['Winter', 'Spring', 'Summer', 'Fall'];
            const mentionedSeasons = seasons.filter(s => 
                text.toLowerCase().includes(s.toLowerCase())
            );
            if (mentionedSeasons.length >= 2) {
                response += generateComparison(mentionedSeasons[0], mentionedSeasons[1]) + '\n\n';
            }
        }

        // Add other pattern responses...
        if (patterns.includes('statistics')) {
            response += `Basic Statistics:\n` +
                       `Average Usage: ${mlAnalysis.basicStatistics.usage.mean.toFixed(2)} kWh\n` +
                       `Standard Deviation: ${mlAnalysis.basicStatistics.usage.std.toFixed(2)} kWh\n` +
                       `Cost per kWh: $${mlAnalysis.basicStatistics.cost.perKwh.toFixed(4)}\n`;
        }

        if (patterns.includes('efficiency')) {
            response += `Model Performance Metrics:\n` +
                       `R² Score (Training): ${mlAnalysis.modelPerformance.r2_training}\n` +
                       `R² Score (Testing): ${mlAnalysis.modelPerformance.r2_testing}\n` +
                       `Most Important Features:\n` +
                       Object.entries(mlAnalysis.modelPerformance.featureImportance)
                           .map(([feature, importance]) => 
                               `- ${feature}: ${(importance * 100).toFixed(1)}%`
                           ).join('\n');
        }

        return response || "I'm not sure how to help with that. Try asking about statistics or visualizations.";
    }

    // Add this function to test if Chart.js is loaded
    function isChartJsLoaded() {
        return typeof Chart !== 'undefined';
    }

    // Check if Chart.js is loaded
    console.log('Chart.js loaded:', isChartJsLoaded());
    
    // Test visualization container
    const vizContainer = document.getElementById('visualizationContainer');
    console.log('Visualization container:', vizContainer);

    // Add explicit visualization test function
    function testVisualization() {
        console.log('Testing visualization...');
        const container = getVisualizationContainer();
        console.log('Visualization container:', container);
        
        // Test creating a simple chart
        const testData = {
            type: 'bar',
            labels: ['Test1', 'Test2', 'Test3'],
            data: [10, 20, 30],
            title: 'Test Chart'
        };
        
        try {
            createChart(
                testData.type,
                testData.data,
                testData.labels,
                testData.title
            );
            console.log('Test chart created successfully');
        } catch (error) {
            console.error('Error creating test chart:', error);
        }
    }

    // Modified sendMessage function with explicit debug logs
    async function sendMessage(text) {
        try {
            console.log('Processing message:', text);
            const patterns = analyzeQuery(text);
            console.log('Detected patterns:', patterns);
            
            if (patterns.length > 0) {
                console.log('Formatting response for patterns');
                const response = formatResponse(patterns, text);
                console.log('Response:', response);
                
                if (response.visualization) {
                    console.log('Visualization data:', response.visualization);
                    // Force visualization container to be visible
                    const vizContainer = document.getElementById('visualizationContainer');
                    vizContainer.style.display = 'block';
                    
                    createChart(
                        response.visualization.type,
                        response.visualization.data,
                        response.visualization.labels,
                        response.visualization.title
                    );
                }
                
                return response.text || "I've created a visualization based on your request.";
            }

            // Proceed with regular chat API call if no analysis patterns matched
            const payload = { text: text };
            const apiResponse = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!apiResponse.ok) throw new Error('Network response was not ok');
            const data = await apiResponse.json();
            return data.reply;

        } catch (error) {
            console.error('Error in sendMessage:', error);
            return 'Sorry, I encountered an error processing your request.';
        }
    }

    // Enhanced message display
    function addMessage(text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        
        // Add specific class based on who sent the message
        if (text.startsWith('User:')) {
            messageDiv.classList.add('user');
        } else if (text.startsWith('Analyst:')) {
            messageDiv.classList.add('analyst');
        }
        
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

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
        chatForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const message = chatInput.value.trim();
            
            if (message) {
                // Add user message
                addMessage('User: ' + message);
                
                // Process the message
                processMessage(message);
                
                // Clear input
                chatInput.value = '';
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

    function processMessage(message) {
        // Your existing message processing logic
        const patterns = analyzeQuery(message.toLowerCase());
        const response = formatResponse(patterns, message);
        addMessage('Analyst: ' + response);
    }
}); 