#!/usr/bin/env python3
"""
Smart Bin AI - Sample Data Generator
This script sends sample data to the Smart Bin AI backend for testing purposes.

Usage:
    python3 sample_data.py
"""

import requests
import json
from datetime import datetime, timedelta
import random
import time

# Configuration
API_URL = "http://localhost:8000"
API_KEY = "smwis-key-2024"

# Sample data
BINS = ["BIN-01", "BIN-02", "BIN-03"]
DISHES = {
    "Rice": 50.0,
    "Curry": 30.0,
    "Chapati": 40.0,
    "Dal": 25.0,
    "Vegetables": 35.0
}

MEALS = ["breakfast", "lunch", "dinner"]

def send_request(endpoint, method="GET", data=None):
    """Send API request"""
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        if method == "POST":
            response = requests.post(f"{API_URL}{endpoint}", json=data, headers=headers, timeout=5)
        else:
            response = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=5)

        if response.status_code in [200, 201]:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

def test_connection():
    """Test if server is running"""
    print("Testing connection...")
    success, result = send_request("/health")

    if success:
        print(f"✅ Server is online!")
        print(f"   Total readings: {result.get('readings', 0)}")
        return True
    else:
        print(f"❌ Cannot connect to {API_URL}")
        print(f"   Make sure Python backend is running: python3 smwis.py")
        return False

def set_cooked_amounts():
    """Set total cooked amounts for each dish"""
    print("\nSetting cooked amounts...")

    for dish, amount in DISHES.items():
        success, result = send_request("/set-cooked", "POST", {
            "dish": dish,
            "total_cooked_kg": amount
        })

        if success:
            print(f"  ✅ {dish}: {amount}kg")
        else:
            print(f"  ❌ {dish}: Error - {result}")

def generate_sample_readings(num_readings=20):
    """Generate and send sample waste readings"""
    print(f"\nGenerating {num_readings} sample readings...")

    for i in range(num_readings):
        bin_id = random.choice(BINS)
        dish = random.choice(list(DISHES.keys()))
        weight = round(random.uniform(0.5, 3.5), 2)
        battery = round(random.uniform(3.7, 4.2), 1)
        rssi = random.randint(-70, -30)

        data = {
            "bin_id": bin_id,
            "dish": dish,
            "weight_kg": weight,
            "battery_voltage": battery,
            "wifi_rssi": rssi
        }

        success, result = send_request("/data", "POST", data)

        if success:
            print(f"  ✅ Reading {i+1}: {bin_id} - {dish} ({weight}kg)")
        else:
            print(f"  ❌ Reading {i+1}: Error - {result}")

        # Small delay to spread out readings over time
        time.sleep(0.5)

def show_analytics():
    """Show current analytics"""
    print("\n" + "="*50)
    print("ANALYTICS DASHBOARD")
    print("="*50)

    endpoints = {
        "Health": "/health",
        "Waste Analyzer": "/analyzer",
        "Pattern Detection": "/patterns",
        "Crowd Velocity": "/crowd",
        "Efficiency Score": "/efficiency",
        "Predictions": "/predict"
    }

    for name, endpoint in endpoints.items():
        success, result = send_request(endpoint)

        if success:
            print(f"\n📊 {name}:")
            print(json.dumps(result, indent=2))
        else:
            print(f"\n❌ {name}: Error")

def main():
    """Main function"""
    print("\n" + "="*50)
    print("Smart Bin AI - Sample Data Generator")
    print("="*50)

    # Test connection
    if not test_connection():
        print("\n❌ Cannot proceed without server connection")
        return

    # Ask user for action
    print("\nOptions:")
    print("1. Generate sample data (default)")
    print("2. Set cooked amounts only")
    print("3. Show current analytics")
    print("4. Do all of the above")

    choice = input("\nSelect option (1-4, default 1): ").strip() or "1"

    try:
        choice = int(choice)
    except:
        choice = 1

    if choice in [2, 4]:
        set_cooked_amounts()

    if choice in [1, 4]:
        generate_sample_readings(20)

    if choice in [3, 4, 1]:
        show_analytics()

    print("\n✅ Sample data generation complete!")
    print("\nNext steps:")
    print("1. Open the frontend in your browser:")
    print("   /Users/raajmohan/Documents/VS Code/HTML/index.html")
    print("2. Check the Dashboard and Analytics tabs")
    print("3. Try adding more readings from different bins/dishes")
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
