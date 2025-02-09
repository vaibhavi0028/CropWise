import pandas as pd
import numpy as np
import requests
import math
import random
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import xgboost as xgb
import joblib
from datetime import datetime, timedelta

# Load the trained model, label encoders, and scaler
xgb_model = joblib.load('/content/xgboost_smart_irrigation_model.pkl')  # Replace with your model file path
label_encoders = joblib.load('/content/label_encoders.pkl')  # Replace with your label encoders file path
scaler = joblib.load('/content/scaler.pkl')  # Replace with your scaler file path

# IP geolocation API key (replace with your API key if required)
IPINFO_API_KEY = "your_ipinfo_api_key"  # Optional, as the free tier works without an API key

# Crop conditions dictionary
crop_conditions = {
    "Arecanut": {"suitable_soil": ["Laterite", "Red", "Loam"], "optimal_humidity": (70, 90), "optimal_temperature": (20, 35), "optimal_soil_moisture": (60, 80)},
    "Banana": {"suitable_soil": ["Alluvial", "Loam", "Clay"], "optimal_humidity": (60, 80), "optimal_temperature": (20, 35), "optimal_soil_moisture": (50, 70)},
    "Black Pepper": {"suitable_soil": ["Laterite", "Loam", "Forest"], "optimal_humidity": (70, 90), "optimal_temperature": (20, 35), "optimal_soil_moisture": (60, 80)},
    "Cashewnut": {"suitable_soil": ["Laterite", "Red"], "optimal_humidity": (60, 80), "optimal_temperature": (20, 35), "optimal_soil_moisture": (50, 70)},
    "Coconut": {"suitable_soil": ["Alluvial", "Loam"], "optimal_humidity": (70, 90), "optimal_temperature": (25, 35), "optimal_soil_moisture": (60, 80)},
    "Dry Chillies": {"suitable_soil": ["Red", "Loam", "Alluvial"], "optimal_humidity": (50, 70), "optimal_temperature": (20, 35), "optimal_soil_moisture": (50, 70)},
    "Ginger": {"suitable_soil": ["Loam", "Alluvial", "Laterite"], "optimal_humidity": (70, 90), "optimal_temperature": (20, 30), "optimal_soil_moisture": (60, 80)},
    "Rice": {"suitable_soil": ["Alluvial", "Clay", "Loam"], "optimal_humidity": (70, 90), "optimal_temperature": (20, 35), "optimal_soil_moisture": (60, 80)},
    "Sugarcane": {"suitable_soil": ["Alluvial", "Loam", "Black"], "optimal_humidity": (60, 80), "optimal_temperature": (20, 35), "optimal_soil_moisture": (50, 70)},
}

# Weather types dictionary
weather_types = {
    "Sunny": (0, 5),         # Rainfall in mm (0–5 mm)
    "Cloudy": (5, 15),       # Rainfall in mm (5–15 mm)
    "Rainy": (15, 50),       # Rainfall in mm (15–50 mm)
    "Heavy Rain": (50, 100), # Rainfall in mm (50–100 mm)
}

# Function to get coordinates from IP address
def get_coordinates_from_ip():
    url = f"https://ipinfo.io?token=Your_TOKEN" if IPINFO_API_KEY else "https://ipinfo.io"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch IP geolocation data: {response.status_code}")
    
    data = response.json()
    lat, lon = data["loc"].split(",")
    return float(lat), float(lon)

# Function to map rainfall to weather type
def map_weather_type(rainfall):
    for weather, (min_rain, max_rain) in weather_types.items():
        if min_rain <= rainfall < max_rain:
            return weather
    return "Heavy Rain"  # Default for rainfall >= 100 mm

# Function to fetch weather data using Open-Meteo API
def get_weather_data(lat, lon):
    # Fetch current weather and forecast
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation&hourly=temperature_2m,relative_humidity_2m,precipitation"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch weather data: {response.status_code}")
    
    data = response.json()
    current = data["current"]
    hourly = data["hourly"]

    # Current weather
    current_temp = current["temperature_2m"]
    current_humidity = current["relative_humidity_2m"]
    current_rainfall = current["precipitation"]

    # Future weather (next 24 hours)
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_index = tomorrow.hour  # Index for the same hour tomorrow
    future_rainfall = hourly["precipitation"][tomorrow_index]

    # Map rainfall to weather types
    current_weather = map_weather_type(current_rainfall)
    future_weather = map_weather_type(future_rainfall)

    return {
        "Weather_now": current_weather,
        "future_weather": future_weather,
        "temperature": current_temp,
        "humidity": current_humidity,
        "rainfall": current_rainfall,
    }

# Function to calculate Haversine distance (for slope calculation)
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Function to calculate runoff depth using SCS Curve Number Method
def runoff(P, CN):
    S = (25400 / CN) - 254  # Potential maximum retention
    if P > 0.2 * S:
        Q = ((P - 0.2 * S)**2) / (P + 0.8 * S)  # Runoff depth (mm)
    else:
        Q = 0
    return Q

# Function to preprocess new data
def preprocess_new_data(new_data, label_encoders, scaler):
    # Encode categorical features
    for col in ["crop_name", "soil_type", "Weather_now", "future_weather"]:
        le = label_encoders[col]
        new_data[col] = le.transform(new_data[col])
    
    # Extract optimal_soil_moisture bounds
    new_data["optimal_soil_moisture_lower"] = new_data["optimal_soil_moisture"].apply(lambda x: float(x.strip("()").split(",")[0]))
    new_data["optimal_soil_moisture_upper"] = new_data["optimal_soil_moisture"].apply(lambda x: float(x.strip("()").split(",")[1]))
    new_data.drop(columns=["optimal_soil_moisture"], inplace=True)
    
    # Normalize numerical features
    numerical_cols = ["soil_moisture", "optimal_humidity", "optimal_temperature", "rainfall", "optimal_soil_moisture_lower", "optimal_soil_moisture_upper", "slope", "runoff_depth"]
    new_data[numerical_cols] = scaler.transform(new_data[numerical_cols])
    
    return new_data

# Function to predict irrigation decision
def predict_irrigation(input_data):
    # Get coordinates from IP address
    lat, lon = get_coordinates_from_ip()
    
    # Fetch weather data
    weather_data = get_weather_data(lat, lon)
    
    # Fetch optimal conditions for the crop
    crop_name = input_data["crop_name"]
    optimal_humidity = crop_conditions[crop_name]["optimal_humidity"]
    optimal_temperature = crop_conditions[crop_name]["optimal_temperature"]
    optimal_soil_moisture = crop_conditions[crop_name]["optimal_soil_moisture"]
    
    # Fetch elevation data for two nearby points to calculate slope
    lat1, lon1 = lat, lon
    lat2, lon2 = lat1 + random.uniform(-0.01, 0.01), lon1 + random.uniform(-0.01, 0.01)  # Nearby point
    h1 = get_elevation(lat1, lon1)
    h2 = get_elevation(lat2, lon2)
    
    # Calculate slope
    d = haversine_distance(lat1, lon1, lat2, lon2)
    slope = ((h2 - h1) / d) * 100  # Slope in percentage
    
    # Calculate runoff depth
    CN = 80 if input_data["soil_type"] in ["Clay", "Black"] else 70 if input_data["soil_type"] in ["Loam", "Alluvial"] else 60
    if slope > 10: CN += 5
    elif slope < 5: CN -= 5
    runoff_depth = runoff(weather_data["rainfall"], CN)
    
    # Prepare input data for the model
    input_data.update({
        "optimal_humidity": optimal_humidity[0],  # Use lower bound of optimal humidity
        "optimal_temperature": optimal_temperature[0],  # Use lower bound of optimal temperature
        "optimal_soil_moisture": f"({optimal_soil_moisture[0]}, {optimal_soil_moisture[1]})",
        "Weather_now": weather_data["Weather_now"],
        "future_weather": weather_data["future_weather"],
        "rainfall": weather_data["rainfall"],
        "slope": slope,
        "runoff_depth": runoff_depth,
    })
    # Convert input data to DataFrame
    new_data = pd.DataFrame([input_data])
    
    # Preprocess the new data
    new_data_processed = preprocess_new_data(new_data, label_encoders, scaler)
    
    # Make predictions
    prediction = xgb_model.predict(new_data_processed)
    
    # Convert prediction to "Yes" or "No"
    return "Yes" if prediction[0] == 1 else "No"

# Example input data
input_data = {
    "crop_name": "Rice",
    "soil_type": "Alluvial",
    "soil_moisture": 60.0,
}

# Predict irrigation decision
decision = predict_irrigation(input_data)
print(f"Should the pump run? {decision}")




'''crop_names = [
    "Arecanut", "Banana", "Black Pepper", "Cashewnut", "Coconut", "Dry Chillies", "Ginger", "Rice",
    "Sugarcane", "Sweet Potato", "Arhar/Tur", "Bajra", "Castor Seed", "Cotton (Lint)", "Gram",
    "Groundnut", "Horse-gram", "Jowar", "Maize", "Moong (Green Gram)", "Onion", "Potato", "Ragi",
    "Rapeseed & Mustard", "Safflower", "Sesamum", "Soyabean", "Sunflower", "Tobacco", "Turmeric",
    "Urad", "Wheat", "Jute", "Masoor", "Barley", "Garlic", "Cardamom", "Coriander", "Cowpea (Lobia)",
    "Tapioca", "Tea", "Coffee", "Rubber", "Mango", "Citrus Fruits", "Pulses"
]

soil_retention = {
    "Alluvial",  # Moderate retention
    "Black",     # High retention
    "Red",        # Low retention
    "Laterite" , # Low retention
    "Arid"      ,# Very low retention
    "Forest"   , # Moderate retention
    "Loam"     , # Moderate to high retention
    "Clay"       # High retention
}'''