# Smart Bin AI — Frontend Setup & Usage Guide

## Overview
This is a complete frontend dashboard for the Smart Bin AI system - an intelligent food waste and flow optimization system. The frontend communicates with the Python backend API via HTTP requests.

## What You Have

### Files Created:
1. **index.html** - Main dashboard interface
2. **styles.css** - Dark-themed styling
3. **script.js** - API integration and interactivity
4. **README.md** - This file

## Prerequisites

### Python Modules (Already Installed)
```bash
pip3 install matplotlib
```

**Also required (usually pre-installed):**
- json (std library)
- http.server (std library)
- datetime (std library)
- collections (std library)

## How to Run

### Step 1: Start the Python Backend
Open a terminal and navigate to the directory containing `smwis.py`:

```bash
cd /Users/raajmohan/Downloads
python3 smwis.py
```

You should see:
```
=======================================================
  Smart Bin AI — Waste & Flow Optimization System
=======================================================
  Server → http://0.0.0.0:8000

  ESP32 Endpoints:
  POST /data          ← ESP32 sends weight here
  POST /set-cooked    ← Mess staff sets cooked qty

  Intelligence Layers:
  GET  /analyzer      ← Layer 2: Waste analysis
  GET  /patterns      ← Layer 3: Pattern detection
  GET  /crowd         ← Layer 4: Crowd velocity
  GET  /predict       ← Layer 5: Cooking predictions
  GET  /efficiency    ← Layer 6: Efficiency score
  GET  /graphs        ← Generate Layer 3 & 4 graphs
  GET  /dashboard     ← All layers at once
=======================================================
```

### Step 2: Open the Frontend
Open a web browser and navigate to:
```
/Users/raajmohan/Documents/VS Code/HTML/index.html
```

Or open it directly from your file system using your browser's "Open File" option.

## Dashboard Features

### Connection & Settings
- **API URL**: Default is `http://localhost:8000`
- **API Key**: Default is `smwis-key-2024`
- **Test Connection**: Verify the backend is running

### Dashboard Tabs

#### 1. **Dashboard**
Overview of all analytics in one place:
- Waste by meal (breakfast, lunch, dinner)
- Waste by dish (rice, curry, etc.)
- Efficiency scores
- Waste percentages

#### 2. **Input Data**
Add readings from ESP32 devices:
- **Bin ID**: Unique identifier for the bin (e.g., BIN-01)
- **Dish**: Name of the dish (e.g., Rice, Curry, Chapati)
- **Weight (kg)**: Waste weight detected
- **Battery Voltage**: Optional device health info
- **WiFi RSSI**: Optional signal strength

Also set cooking totals so the system can calculate waste percentages.

#### 3. **Analysis**
Detailed waste analysis:
- Total waste breakdown
- Percentage calculations for each dish
- Efficiency scores (100% = no waste, 0% = complete waste)

#### 4. **Patterns**
AI-detected patterns:
- **Over-serving**: High waste in first 15 minutes of meal
- **Unpopular dishes**: Dishes with waste > 30%
- **Low attendance**: Weekend vs weekday differences

#### 5. **Crowd Analytics**
Real-time crowd monitoring:
- **Velocity**: kg/min rate of waste (indicates crowd size)
- **Crowd Status**: "Light", "Normal", or "Heavy crowd"
- **Per-bin velocity**: Individual bin analysis
- **Alerts**: Warning if heavy crowd detected

#### 6. **Predictions**
Machine learning recommendations:
- Needs 7+ days of data to activate
- Suggests reducing cooking by 10% for high-waste dishes
- Shows trend analysis (increasing/decreasing waste)

### Quick Stats
Real-time metrics displayed at the top:
- Total Readings: Number of waste entries
- Server Status: Online/Offline
- Efficiency Score: Overall system efficiency
- Active Bins: Number of unique bins

### Auto-Refresh
- Automatically updates every 10 seconds
- Toggle on/off with the checkbox
- Saves preference to browser storage

## Example Workflow

### 1. Initial Setup
```
1. Start Python backend (smwis.py)
2. Open frontend in browser
3. Verify "Server Status" shows "Online"
4. Click "Test Connection" to confirm
```

### 2. Add Operational Data
```
1. Go to "Input Data" tab
2. Set cooked amounts first:
   - Dish: "Rice"
   - Total Cooked: 50 kg
   - Set Cooked Amount

   - Dish: "Curry"
   - Total Cooked: 30 kg
   - Set Cooked Amount
```

### 3. Record Waste
```
1. Go to "Input Data" tab
2. Add readings as waste is detected:
   - Bin ID: BIN-01
   - Dish: Rice
   - Weight: 2.5 kg
   - Add Reading
```

### 4. Monitor Patterns
```
1. Go to "Patterns" tab
2. Check for detected issues
3. Go to "Crowd Analytics" to see velocity
4. After 7+ days, check "Predictions" for recommendations
```

## API Endpoints Reference

### Data Collection (POST)
```
POST /data
Headers: {"X-API-Key": "smwis-key-2024"}
Body: {
  "bin_id": "BIN-01",
  "dish": "Rice",
  "weight_kg": 2.5,
  "battery_voltage": 4.1,
  "wifi_rssi": -45
}
```

```
POST /set-cooked
Headers: {"X-API-Key": "smwis-key-2024"}
Body: {
  "dish": "Rice",
  "total_cooked_kg": 50.0
}
```

### Intelligence Layers (GET)
```
GET /analyzer         → Waste analysis
GET /patterns         → Pattern detection
GET /crowd            → Crowd velocity
GET /predict          → Cooking predictions
GET /efficiency       → Efficiency scores
GET /graphs           → Generate matplotlib graphs
GET /dashboard        → All data at once
GET /health           → Server status
GET /readings         → Last 50 readings
```

## Data Persistence

Currently, all data is stored **in memory**. This means:
- Data persists while the server is running
- Data is lost when you restart the Python server
- To use persistent storage, modify the Python code to connect to a database (MySQL, PostgreSQL, etc.)

### To Connect a Database
Edit `smwis.py` and replace the `>>> DB CONNECTION PLACEHOLDER <<<` sections with your database connection code.

## Browser Compatibility
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support

## Troubleshooting

### "Offline" Status
1. Check if Python backend is running
2. Verify API URL is correct (default: http://localhost:8000)
3. Check if port 8000 is not blocked by firewall

### No Data Showing
1. Add readings via "Input Data" tab
2. Set cooked amounts before adding readings
3. Check browser console for errors (F12 → Console)

### Settings Not Saving
1. Browser local storage might be disabled
2. Try clearing browser cache
3. Check if you're in private/incognito mode

## Customization

### Change Colors
Edit `styles.css` and modify the `:root` variables:
```css
:root {
    --primary: #00d4aa;        /* Main green */
    --secondary: #ff6b35;      /* Orange */
    --warning: #ffd166;        /* Yellow */
    --danger: #ef4444;         /* Red */
    --success: #10b981;        /* Green */
    ...
}
```

### Change Auto-Refresh Interval
Edit `script.js`, find the `startAutoRefresh()` function:
```javascript
setInterval(() => {
    // ...
}, 10000);  // Change 10000 to desired milliseconds
```

### Change Thresholds
Edit Python backend in `smwis.py`:
```python
OVERSERVING_THRESHOLD = 0.40      # if >40% waste in first 15 mins
UNPOPULAR_DISH_THRESHOLD = 0.30   # if dish waste >30%
CROWD_VELOCITY_THRESHOLD = 0.5    # kg/min
```

## Support

For issues with:
- **Frontend**: Check browser console (F12)
- **Backend**: Check Python terminal output
- **Connection**: Verify both are on same network

## Features Summary

✅ Real-time dashboard
✅ 6 Intelligence Layers
✅ Pattern detection
✅ Crowd analysis
✅ Predictive recommendations
✅ Data persistence (in memory)
✅ API key authentication
✅ Auto-refresh functionality
✅ Responsive design
✅ Dark theme
✅ No external dependencies (pure HTML/CSS/JS)
✅ Easy database integration

---

**Smart Bin AI v1.0** — Intelligent Food Waste & Flow Optimization
