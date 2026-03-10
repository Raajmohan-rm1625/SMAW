// Configuration
let API_URL = 'http://localhost:8000';
let API_KEY = 'smwis-key-2024';
let autoRefreshInterval = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Load saved settings
    loadSettings();

    // Setup event listeners
    setupEventListeners();

    // Initial connection test
    testConnection();

    // Start auto-refresh
    startAutoRefresh();
});

// Setup Event Listeners
function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            switchTab(this.getAttribute('data-tab'));
        });
    });

    // Forms
    document.getElementById('readingForm').addEventListener('submit', handleReadingSubmit);
    document.getElementById('cookedForm').addEventListener('submit', handleCookedSubmit);

    // Settings
    document.getElementById('apiUrl').addEventListener('change', function() {
        API_URL = this.value;
        localStorage.setItem('apiUrl', API_URL);
    });

    document.getElementById('apiKey').addEventListener('change', function() {
        API_KEY = this.value;
        localStorage.setItem('apiKey', API_KEY);
    });

    // Auto-refresh toggle
    document.getElementById('autoRefresh').addEventListener('change', function() {
        localStorage.setItem('autoRefresh', this.checked);
        if (this.checked) {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });
}

// Tab Management
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });

    // Deactivate all buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName).classList.add('active');

    // Activate selected button
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Refresh data for tab if needed
    if (tabName === 'analysis') {
        updateAnalysisTab();
    } else if (tabName === 'patterns') {
        updatePatternsTab();
    } else if (tabName === 'crowd') {
        updateCrowdTab();
    } else if (tabName === 'predictions') {
        updatePredictionsTab();
    } else if (tabName === 'data-input') {
        updateReadingsTable();
    }
}

// Load Settings
function loadSettings() {
    const savedUrl = localStorage.getItem('apiUrl');
    const savedKey = localStorage.getItem('apiKey');
    const savedAutoRefresh = localStorage.getItem('autoRefresh');

    if (savedUrl) {
        API_URL = savedUrl;
        document.getElementById('apiUrl').value = API_URL;
    }

    if (savedKey) {
        API_KEY = savedKey;
        document.getElementById('apiKey').value = API_KEY;
    }

    if (savedAutoRefresh !== null) {
        document.getElementById('autoRefresh').checked = savedAutoRefresh === 'true';
    }
}

// API Function
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-API-Key': API_KEY
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const jsonData = await response.json();

        if (!response.ok) {
            console.error('API Error:', jsonData);
            return null;
        }

        return jsonData;
    } catch (error) {
        console.error('Fetch Error:', error);
        return null;
    }
}

// Test Connection
async function testConnection() {
    const result = await apiCall('/health');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    if (result) {
        statusIndicator.classList.add('online');
        statusText.textContent = 'Online';
        document.getElementById('serverStatus').textContent = 'Online';

        // Update stats
        document.getElementById('totalReadings').textContent = result.readings || 0;
    } else {
        statusIndicator.classList.remove('online');
        statusText.textContent = 'Offline';
        document.getElementById('serverStatus').textContent = 'Offline';
    }
}

// Refresh All Data
async function refreshAllData() {
    await testConnection();

    if (document.querySelector('.tab-pane.active').id === 'dashboard') {
        updateDashboardTab();
    } else if (document.querySelector('.tab-pane.active').id === 'analysis') {
        updateAnalysisTab();
    } else if (document.querySelector('.tab-pane.active').id === 'patterns') {
        updatePatternsTab();
    } else if (document.querySelector('.tab-pane.active').id === 'crowd') {
        updateCrowdTab();
    } else if (document.querySelector('.tab-pane.active').id === 'predictions') {
        updatePredictionsTab();
    } else if (document.querySelector('.tab-pane.active').id === 'data-input') {
        updateReadingsTable();
    }
}

// Dashboard Tab Update
async function updateDashboardTab() {
    const analyzer = await apiCall('/analyzer');
    const efficiency = await apiCall('/efficiency');

    if (analyzer) {
        // Waste by Meal
        displayDataBlock('wasteByMeal', analyzer.waste_by_meal || {});

        // Waste by Dish
        displayDataBlock('wasteByDish', analyzer.waste_by_dish || {});

        // Efficiency
        displayDataBlock('efficiencyByDish', analyzer.efficiency_score || {});

        // Waste Percent
        displayDataBlock('wastePercent', analyzer.waste_percent || {});
    }

    if (efficiency && efficiency.efficiency_score) {
        document.getElementById('efficiencyScore').textContent = efficiency.efficiency_score + '%';
    }
}

// Analysis Tab Update
async function updateAnalysisTab() {
    const analyzer = await apiCall('/analyzer');

    if (analyzer && analyzer.message === undefined) {
        displayDataBlock('analyzerWasteByMeal', analyzer.waste_by_meal || {});
        displayDataBlock('analyzerWasteByDish', analyzer.waste_by_dish || {});
        displayDataBlock('analyzerWastePercent', analyzer.waste_percent || {});
        displayDataBlock('analyzerEfficiency', analyzer.efficiency_score || {});
    }
}

// Patterns Tab Update
async function updatePatternsTab() {
    const patterns = await apiCall('/patterns');

    if (patterns && patterns.patterns) {
        const container = document.getElementById('patternsContainer');
        container.innerHTML = '';

        if (patterns.patterns_found === 0 || (patterns.patterns.length === 1 && patterns.patterns[0].type === 'OK')) {
            container.innerHTML = '<div class="pattern-item ok"><div class="pattern-message">✅ No unusual patterns detected</div></div>';
        } else {
            patterns.patterns.forEach(pattern => {
                const elem = document.createElement('div');
                elem.className = `pattern-item ${pattern.severity || 'info'}`;
                elem.innerHTML = `
                    <div class="pattern-type">${pattern.type}</div>
                    <div class="pattern-message">${pattern.message}</div>
                `;
                container.appendChild(elem);
            });
        }
    }
}

// Crowd Tab Update
async function updateCrowdTab() {
    const crowd = await apiCall('/crowd');

    if (crowd) {
        document.getElementById('avgVelocity').textContent =
            (crowd.velocity_kg_per_min || 0) + ' kg/min';
        document.getElementById('crowdStatus').textContent =
            (crowd.crowd_status || 'Unknown').toUpperCase();
        document.getElementById('velocityThreshold').textContent =
            (crowd.threshold_kg_per_min || 0) + ' kg/min';

        // Display alert if exists
        if (crowd.alert) {
            const alertDiv = document.getElementById('crowdAlert');
            alertDiv.textContent = crowd.alert;
            alertDiv.style.display = 'block';
        } else {
            document.getElementById('crowdAlert').style.display = 'none';
        }

        // Per-bin velocity
        displayDataBlock('perBinVelocity', crowd.per_bin_velocity || {});
    }
}

// Predictions Tab Update
async function updatePredictionsTab() {
    const predict = await apiCall('/predict');

    if (predict) {
        const container = document.getElementById('predictionsContainer');
        container.innerHTML = '';

        if (predict.message) {
            container.innerHTML = `<div class="alert alert-warning">${predict.message}</div>`;
        }

        if (predict.recommendations && predict.recommendations.length > 0) {
            predict.recommendations.forEach(rec => {
                if (rec.message) {
                    container.innerHTML = `<div class="alert alert-warning">${rec.message}</div>`;
                    return;
                }

                const elem = document.createElement('div');
                elem.className = 'prediction-item';
                elem.innerHTML = `
                    <div class="prediction-header">${rec.dish}</div>
                    <div class="prediction-detail">
                        <span class="label">Avg Waste:</span>
                        <span class="value">${rec.avg_waste_kg} kg</span>
                    </div>
                    <div class="prediction-detail">
                        <span class="label">Waste %:</span>
                        <span class="value">${rec.waste_percent}%</span>
                    </div>
                    <div class="prediction-detail">
                        <span class="label">Trend:</span>
                        <span class="value">${rec.trend}</span>
                    </div>
                    <div class="prediction-recommendation">
                        🎯 ${rec.recommendation}
                    </div>
                `;
                container.appendChild(elem);
            });
        }
    }
}

// Readings Table Update
async function updateReadingsTable() {
    const readings = await apiCall('/readings');

    if (readings && readings.readings) {
        const container = document.getElementById('recentReadings');
        container.innerHTML = '';

        if (readings.readings.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No readings yet</p>';
            return;
        }

        // Header
        const header = document.createElement('div');
        header.className = 'reading-row reading-header';
        header.innerHTML = `
            <div>Bin ID</div>
            <div>Dish</div>
            <div>Weight (kg)</div>
            <div>Meal</div>
            <div>Time</div>
        `;
        container.appendChild(header);

        // Rows
        readings.readings.slice().reverse().forEach(reading => {
            const row = document.createElement('div');
            row.className = 'reading-row';
            row.innerHTML = `
                <div class="reading-cell">${reading.bin_id || '-'}</div>
                <div class="reading-cell">${reading.dish || '-'}</div>
                <div class="reading-cell">${reading.weight_kg || '-'}</div>
                <div class="reading-cell">${reading.meal || '-'}</div>
                <div class="reading-cell">${reading.timestamp || '-'}</div>
            `;
            container.appendChild(row);
        });
    }
}

// Display Data Block
function displayDataBlock(elementId, data) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';

    if (!data || Object.keys(data).length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary);">No data available</p>';
        return;
    }

    Object.entries(data).forEach(([key, value]) => {
        const div = document.createElement('div');
        const displayValue = typeof value === 'number' ? value.toFixed(2) : value;
        div.innerHTML = `
            <span class="label">${key}:</span>
            <span class="value">${displayValue}</span>
        `;
        container.appendChild(div);
    });
}

// Form Handlers
async function handleReadingSubmit(e) {
    e.preventDefault();

    const data = {
        bin_id: document.getElementById('binId').value,
        dish: document.getElementById('dish').value,
        weight_kg: parseFloat(document.getElementById('weightKg').value),
        battery_voltage: document.getElementById('batteryVoltage').value ?
            parseFloat(document.getElementById('batteryVoltage').value) : null,
        wifi_rssi: document.getElementById('wifiRssi').value ?
            parseInt(document.getElementById('wifiRssi').value) : null
    };

    const result = await apiCall('/data', 'POST', data);

    if (result) {
        alert('✅ Reading added successfully!');
        document.getElementById('readingForm').reset();
        updateReadingsTable();
        refreshAllData();
    } else {
        alert('❌ Error adding reading');
    }
}

async function handleCookedSubmit(e) {
    e.preventDefault();

    const data = {
        dish: document.getElementById('cookedDish').value,
        total_cooked_kg: parseFloat(document.getElementById('cookedAmount').value)
    };

    const result = await apiCall('/set-cooked', 'POST', data);

    if (result) {
        alert('✅ Cooked amount set successfully!');
        document.getElementById('cookedForm').reset();
        refreshAllData();
    } else {
        alert('❌ Error setting cooked amount');
    }
}

// Clear All Data
function clearAllData() {
    if (confirm('Are you sure you want to clear all data? This action cannot be undone.')) {
        alert('Note: To clear data, you need to restart the Python server.\n\nThe server stores data in memory, so restarting it will clear all readings.');
    }
}

// Auto-refresh
function startAutoRefresh() {
    if (autoRefreshInterval) return;

    autoRefreshInterval = setInterval(() => {
        if (document.getElementById('autoRefresh').checked) {
            refreshAllData();
        }
    }, 10000); // 10 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Initialize dashboard on load
document.addEventListener('DOMContentLoaded', function() {
    updateDashboardTab();
});
