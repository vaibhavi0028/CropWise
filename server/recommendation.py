
import joblib
import pickle
import tensorflow as tf
import pandas as pd
import numpy as np
import requests
import asyncio
import aiohttp
from datetime import datetime
from geopy.geocoders import Nominatim

# Load models and data
xgb_model = joblib.load("xgb_model.pkl")
le = joblib.load("label_encoder.pkl")
scaler = joblib.load("scaler.pkl")
hybrid_model = tf.keras.models.load_model("hybrid_model.h5")
data = pd.read_csv("Final.csv").fillna(method='ffill')

# Define constants and mappings
price_cache = {}
CACHE_TTL = 3600  # Cache for 1 hour
CROP_NAME_MAPPING = {
    "Ginger": "Ginger (Dry)",
    "Cowpea (Lobia)": "Cowpea (Lobia/Karamani)",
    "Coriander": "Corriander Seed",
    "Sweet potato": "Sweet Potato"
}

# Define crop prices
crop_prices_per_ton = {
    "Arecanut": 46500,
    "Banana": 12000,
    "Black Pepper": 400000,
    "Cashewnut": 80000,
    "Coconut": 25000,
    "Dry Chillies": 120000,
    "Ginger": 30000,
    "Rice": 25000,
    "Sugarcane": 3500,
    "Sweet potato": 10000,
    "Arhar/Tur": 60000,
    "Bajra": 20000,
    "Castor seed": 50000,
    "Cotton(lint)": 70000,
    "Gram": 50000,
    "Groundnut": 60000,
    "Horse-gram": 40000,
    "Jowar": 25000,
    "Maize": 20000,
    "Moong(Green Gram)": 70000,
    "Onion": 15000,
    "Potato": 10000,
    "Ragi": 30000,
    "Rapeseed & Mustard": 50000,
    "Safflower": 40000,
    "Sesamum": 80000,
    "Soyabean": 40000,
    "Sunflower": 50000,
    "Tobacco": 150000,
    "Turmeric": 80000,
    "Urad": 70000,
    "Wheat": 25000,
    "Jute": 5000,
    "Masoor": 50000,
    "Barley": 20000,
    "Garlic": 40000,
    "Cardamom": 1000000,
    "Coriander": 60000,
    "Cowpea (Lobia)": 40000,
    "Tapioca": 10000,
    "Tomato": 15000,
}

crops= {
    'Arecanut': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 5,
        'temp_factor': 1.05,
        'growth_data': 1825,
        'sun_factor': 0.909,
        'image': 'https://3.imimg.com/data3/YK/QS/MY-11002287/arecanut.jpg'
    },
    'Banana': {
        'temp_min': 28,
        'temp_max': 32,
        'sunlight_hours': 6,
        'temp_factor': 1.1,
        'growth_data': 330,
        'sun_factor': 1.091,
        'image': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?fm=jpg&q=60&w=3000&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8YmFuYW5hc3xlbnwwfHwwfHx8MA%3D%3D'
    },
    'Black Pepper': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 5,
        'temp_factor': 1.1,
        'growth_data': 1200,
        'sun_factor': 0.909,
        'image': 'https://assets.clevelandclinic.org/transform/65ddb397-7835-4b21-b30b-d123be3cb5c8/blackPepper-185067429-770x533-1_jpg'
    },
    'Cashewnut': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 1.2,
        'growth_data': 1600,
        'sun_factor': 1.091,
        'image': 'https://biobasics.org/cdn/shop/files/buy-organic-cashewnut-online-at-bio-basics-store.png?v=1738822315&width=1000'
    },
    'Coconut': {
        'temp_min': 27,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 1.2,
        'growth_data': 2400,
        'sun_factor': 1.091,
        'image': 'https://m.media-amazon.com/images/I/61ZRyCB7o5S.jpg'
    },
    'Dry chillies': {
        'temp_min': 30,
        'temp_max': 35,
        'sunlight_hours': 8,
        'temp_factor': 1.1,
        'growth_data': 180,
        'sun_factor': 1.455,
        'image': 'https://m.media-amazon.com/images/I/51L0Mg0ouDL._AC_UF1000,1000_QL80_.jpg'
    },
    'Ginger': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 4,
        'temp_factor': 1.1,
        'growth_data': 225,
        'sun_factor': 0.727,
        'image': 'https://assets.epicurious.com/photos/58d3fed8e2c8295cfbf4a52f/1:1/w_1333,h_1333,c_limit/ginger_root_pile_23032017.jpg'
    },
    'Rice': {
        'temp_min': 20,
        'temp_max': 35,
        'sunlight_hours': 5,
        'temp_factor': 1.0,
        'growth_data': 150,
        'sun_factor': 0.909,
        'image': 'https://cdn.britannica.com/17/176517-050-6F2B774A/Pile-uncooked-rice-grains-Oryza-sativa.jpg'
    },
    'Sugarcane': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 1.2,
        'growth_data': 360,
        'sun_factor': 1.091,
        'image': 'https://m.media-amazon.com/images/I/81VvA8Tf8kL._AC_UF1000,1000_QL80_.jpg'
    },
    'Sweet potato': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 7,
        'temp_factor': 1.1,
        'growth_data': 120,
        'sun_factor': 1.273,
        'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/58/Ipomoea_batatas_006.JPG/1200px-Ipomoea_batatas_006.JPG'
    },
    'Arhar/Tur': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 7,
        'temp_factor': 1.1,
        'growth_data': 225,
        'sun_factor': 1.273,
        'image': 'https://5.imimg.com/data5/QH/UB/MY-48524887/paddy-rice-500x500.jpg'
    },
    'Bajra': {
        'temp_min': 28,
        'temp_max': 35,
        'sunlight_hours': 8,
        'temp_factor': 1.2,
        'growth_data': 105,
        'sun_factor': 1.455,
        'image': 'https://3.imimg.com/data3/MP/QG/MY-1160301/bajra-seed-500x500.jpg'
    },
    'Castor seed': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 7,
        'temp_factor': 1.2,
        'growth_data': 225,
        'sun_factor': 1.273,
        'image': 'https://rukminim2.flixcart.com/image/850/1000/xif0q/plant-seed/1/2/q/250-ravel-castor-seeds-250gm-ravel-original-imagm5u9ydxfhhgq.jpeg?q=90&crop=false'
    },
    'Cotton(lint)': {
        'temp_min': 25,
        'temp_max': 35,
        'temp_factor': 1.2,
        'growth_data': 165,
        'sun_factor': 1.091,
        'image': 'https://5.imimg.com/data5/SELLER/Default/2021/1/LN/YQ/RY/6278729/cotton-lint-jpg.jpg'
    },
    'Gram': {
        'temp_min': 25,
        'temp_max': 35,
        'sunlight_hours': 6,
        'temp_factor': 0.9,
        'growth_data': 105,
        'sun_factor': 1.091,
        'image': 'https://4.imimg.com/data4/IG/II/MY-27845820/bengal-gram-whole-500x500.jpg'
    },
    'Groundnut': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 7,
        'temp_factor': 1.2,
        'growth_data': 135,
        'sun_factor': 1.273,
        'image': 'https://m.media-amazon.com/images/I/41RoBZdJ+iL._AC_UF1000,1000_QL80_.jpg'
    },
    'Horse-gram': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 1.1,
        'growth_data': 110,
        'sun_factor': 1.091,
        'image': 'https://cdn.prod.website-files.com/65056ba428fdd5501ff0ef16/66a37bd39906e9a6ca6736b8_6622ecb38346f2f86215cc70_AdobeStock_559009411-_1_.webp'
    },
    'Jowar': {
        'temp_min': 25,
        'temp_max': 35,
        'sunlight_hours': 7,
        'temp_factor': 1.1,
        'growth_data': 120,
        'sun_factor': 1.273,
        'image': 'https://5.imimg.com/data5/JD/EG/MY/SELLER-61630555/sorghum-jowar-.jpg'
    },
    'Maize': {
        'temp_min': 20,
        'temp_max': 35,
        'sunlight_hours': 7,
        'temp_factor': 1.2,
        'growth_data': 100,
        'sun_factor': 1.273,
        'image': 'https://farmatma.in/wp-content/uploads/2019/05/maize-cultivation.jpg'
    },
    'Moong(Green Gram)': {
        'temp_min': 25,
        'temp_max': 35,
        'sunlight_hours': 6,
        'temp_factor': 1.0,
        'growth_data': 75,
        'sun_factor': 1.091,
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgnebhTVV1rqF3F_kPsLqBkEUKRKJypgtM_A&s'
    },
    'Onion': {
        'temp_min': 15,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 0.9,
        'growth_data': 165,
        'sun_factor': 1.091,
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRQW7-aAJENmiznbqnQftzp5vCP4GYEiOOFUg&s'
    },
    'Potato': {
        'temp_min': 15,
        'temp_max': 25,
        'sunlight_hours': 6,
        'temp_factor': 0.8,
        'growth_data': 105,
        'sun_factor': 1.091,
        'image': 'https://cdn.mos.cms.futurecdn.net/iC7HBvohbJqExqvbKcV3pP-1200-80.jpg'
    },
    'Ragi': {
        'temp_min': 20,
        'temp_max': 35,
        'sunlight_hours': 6,
        'temp_factor': 1.1,
        'growth_data': 110,
        'sun_factor': 1.091,
        'image': 'https://www.atulyam.co.in/cdn/shop/articles/ragi_picture.jpg?v=1705326736&width=1100'
    },
    'Rapeseed & Mustard': {
        'temp_min': 15,
        'temp_max': 25,
        'sunlight_hours': 6,
        'temp_factor': 1.0,
        'growth_data': 105,
        'sun_factor': 1.091,
        'image': 'https://images.assettype.com/english-sentinelassam/import/h-upload/2023/02/12/438138-mustard.webp'
    },
    'Safflower': {
        'temp_min': 20,
        'temp_max': 30,
        'sunlight_hours': 8,
        'temp_factor': 1.1,
        'growth_data': 135,
        'sun_factor': 1.455,
        'image': 'https://upload.wikimedia.org/wikipedia/commons/7/7f/Safflower.jpg'
    },
    'Sesamum': {
        'temp_min': 25,
        'temp_max': 35,
        'sunlight_hours': 8,
        'temp_factor': 1.1,
        'growth_data': 105,
        'sun_factor': 1.455,
        'image': 'https://cdn.britannica.com/66/212766-050-FF1A49A0/sesame-seeds-wooden-spoon.jpg'
    },
    'Soyabean': {
        'temp_min': 25,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 1.0,
        'growth_data': 110,
        'sun_factor': 1.091,
        'image': 'https://www.mystore.in/s/62ea2c599d1398fa16dbae0a/64ce0821657a7a454d2634aa/soyabean.jpg'
    },
    'Sunflower': {
        'temp_min': 20,
        'temp_max': 35,
        'sunlight_hours': 8,
        'temp_factor': 1.1,
        'growth_data': 100,
        'sun_factor': 1.455,
        'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/40/Sunflower_sky_backdrop.jpg/800px-Sunflower_sky_backdrop.jpg'
    },
    'Tobacco': {
        'temp_min': 25,
        'temp_max': 35,
        'sunlight_hours': 7,
        'temp_factor': 1.2,
        'growth_data': 115,
        'sun_factor': 1.273,
        'image': 'https://upload.wikimedia.org/wikipedia/commons/b/b5/DunhillLightFlake.jpg'
    },
    'Turmeric': {
        'temp_min': 20,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 1.1,
        'growth_data': 225,
        'sun_factor': 0.95,
        'image': 'https://m.media-amazon.com/images/I/6143Jp46RpL._AC_UF1000,1000_QL80_.jpg'
    },
    'Urad': {
        'temp_min': 25,
        'temp_max': 35,
        'sunlight_hours': 5,
        'temp_factor': 1.0,
        'growth_data': 105,
        'sun_factor': 0.9,
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRwkT1pB69S-hAXxuNPS8zyp9l7E4_-UB9MWA&s'
    },
    'Wheat': {
        'temp_min': 10,
        'temp_max': 25,
        'sunlight_hours': 8,
        'temp_factor': 0.9,
        'growth_data': 135,
        'sun_factor': 1.05,
        'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Vehn%C3%A4pelto_6.jpg/640px-Vehn%C3%A4pelto_6.jpg'
    },
    'Jute': {
        'temp_min': 25,
        'temp_max': 38,
        'sunlight_hours': 6,
        'temp_factor': 1.1,
        'growth_data': 135,
        'sun_factor': 1.0,
        'image': 'https://5.imimg.com/data5/SELLER/Default/2023/9/343940612/IB/XU/ZS/50712066/raw-jute-fiber-500x500.jpg'
    },
    'Masoor': {
        'temp_min': 15,
        'temp_max': 25,
        'sunlight_hours': 6,
        'temp_factor': 0.9,
        'growth_data': 110,
        'sun_factor': 0.92,
        'image': 'https://gonefarmers.com/cdn/shop/products/image_cc51f8bf-501f-4ae7-a546-3a579299ca9d_1024x1024@2x.jpg?v=1596652176'
    },
    'Barley': {
        'temp_min': 12,
        'temp_max': 25,
        'sunlight_hours': 8,
        'temp_factor': 0.9,
        'growth_data': 135,
        'sun_factor': 1.03,
        'image': 'https://5.imimg.com/data5/SELLER/Default/2022/12/CA/KF/BC/12585979/whole-barley-grain.jpg'
    },
    'Garlic': {
        'temp_min': 12,
        'temp_max': 24,
        'sunlight_hours': 6,
        'temp_factor': 1.0,
        'growth_data': 195,
        'sun_factor': 0.85,
        'image': 'https://c.ndtvimg.com/2023-09/1ulndeoo_garlic_625x300_13_September_23.jpg?im=FaceCrop,algorithm=dnn,width=620,height=350'
    },
    'Cardamom': {
        'temp_min': 15,
        'temp_max': 35,
        'sunlight_hours': 4,
        'temp_factor': 1.2,
        'growth_data': 1275,
        'sun_factor': 0.88,
        'image': 'https://www.nutrixia.in/cdn/shop/files/cardamom_8mm.jpg?v=1737799658&width=1445'
    },
    'Coriander': {
        'temp_min': 17,
        'temp_max': 27,
        'sunlight_hours': 6,
        'temp_factor': 1.0,
        'growth_data': 105,
        'sun_factor': 0.9,
        'image': 'https://www.khethari.com/cdn/shop/articles/9972fcbe3ad2f6b3b0a6ad37f723e969-520408.jpg?v=1719811388'
    },
    'Cowpea (Lobia)': {
        'temp_min': 20,
        'temp_max': 30,
        'sunlight_hours': 6,
        'temp_factor': 1.1,
        'growth_data': 82,
        'sun_factor': 0.93,
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQhJsIi6Rb76ccAyYlIMjp4iIGAfOnon2CkOg&s'
    },
    'Tapioca': {
        'temp_min': 25,
        'temp_max': 35,
        'sunlight_hours': 7,
        'temp_factor': 1.1,
        'growth_data': 315,
        'sun_factor': 0.97,
        'image': 'https://th-i.thgim.com/public/life-and-style/food/i2ie81/article28181287.ece/alternates/FREE_1200/28TVMTAPIOCACROP'
    },
    'Tomato': {
    'temp_min': 20,
    'temp_max': 30,
    'sunlight_hours': 6,
    'temp_factor': 1.2,
    'growth_data': 320,
    'sun_factor': 0.95,
    'image': 'https://example.com/tomato-plant.jpg'
}
}

# Function to fetch crop price from the first API
def fetch_real_crop_prices_from_first_api(location, crop_name, timeout=10):
    API_KEY = "579b464db66ec23bdd000001822f8e0b12f04cc04e30eff902a405c1"
    base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    params = {
        'api-key': API_KEY,
        'filters[state]': location.split(',')[0].strip(),
        'filters[commodity]': crop_name,
        'format': 'json',
        'limit': 1
    }

    try:
        response = requests.get(base_url, params=params, timeout=timeout)
        if response.status_code == 200:
            data = response.json()
            if data.get('records'):
                return float(data['records'][0]['modal_price'])
        else:
            print(f"API request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

    # If the API fails, fall back to the second function
    print(f"Failed to fetch price for {crop_name} from first API. Using fallback price.")
    return None

# Function to fetch crop price from the second API (MSP)
def fetch_real_crop_prices_from_second_api(location, crop_name):
    if crop_name in crop_prices_per_ton:
        return crop_prices_per_ton[crop_name]
    else:
        print(f"Price for {crop_name} not found in the dictionary.")
        return None  # Return None if crop is not in the dictionary

# Function to get stable price
def get_stable_price(location, crop_name):
    current_hour = datetime.now().hour  # Get current hour (24-hour format)

    # Check if current time is between 10:00 PM and 6:00 AM
    if current_hour >= 22 or current_hour < 10:
        price = fetch_real_crop_prices_from_second_api(location, crop_name)  # Directly use second API
    else:
        # Proceed with the regular process
        cache_key = f"{location}_{crop_name}"
        if cache_key in price_cache:
            cached_price, timestamp = price_cache[cache_key]
            if (pd.Timestamp.now() - timestamp).seconds < CACHE_TTL:
                return cached_price

        price = fetch_real_crop_prices_from_first_api(location, crop_name)
        if price is None:
            price = fetch_real_crop_prices_from_second_api(location, crop_name)  # Use fallback function

        price_cache[cache_key] = (price, pd.Timestamp.now())

    return price

# Function to get coordinates
def get_coordinates(location):
    geolocator = Nominatim(user_agent="geoapi")
    geo_data = geolocator.geocode(location)
    if geo_data:
        return geo_data.latitude, geo_data.longitude
    return None, None

# Function to get elevation
def get_elevation(lat, lon):
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lon}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            elevation = data['results'][0]['elevation']
            return elevation
        else:
            print("Failed to fetch elevation data.")
            return None
    except Exception as e:
        print(f"Error fetching elevation: {e}")
        return None

# Function to classify terrain based on elevation
def classify_terrain(elevation):
    return "Hilly" if elevation and elevation > 500 else "Plain"

# Function to get weather data
def get_weather_data(location):
    latitude, longitude = get_coordinates(location)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current_weather = data['current']

        weather_data = {
            'humidity': current_weather['relative_humidity_2m'],  # Humidity percentage
            'rainfall': current_weather.get('precipitation', 0),  # Rainfall in mm
            'temperature': current_weather.get('temperature_2m', 25)  # Temperature in Celsius
        }

        return weather_data
    else:
        print("Error fetching weather data")
        return None

# Function to fetch current sunlight hours
def fetch_current_sunlight(location):
    latitude, longitude = get_coordinates(location)
    if latitude is None:
        return {"error": "Invalid location"}

    # Get today's date
    today_date = datetime.today().strftime("%Y-%m-%d")

    # Open-Meteo API request for today's sunlight hours
    url = f"https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "sunshine_duration",
        "timezone": "auto",
        "start_date": today_date,
        "end_date": today_date
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "daily" in data and "sunshine_duration" in data["daily"]:
            sunlight_sec = data["daily"]["sunshine_duration"][0]  # Sunshine duration in seconds
            sunlight_min = round(sunlight_sec / 60, 2)  # Convert to minutes
            return {"current_sunlight_hours": sunlight_min / 60}

    return {"error": "Unable to fetch sunlight data"}


columns = [
    'soil_moisture', 'N', 'P', 'K', 'soil_pH', 'temperature', 'humidity',
    'rainfall', 'sunlight_hours', 'last_crop', 'land_size', 'location',
    'crop', 'optimal_N', 'optimal_P', 'optimal_K', 'optimal_pH_min',
    'optimal_pH_max', 'expected_yield'
]

features = [
    'soil_moisture', 'N', 'P', 'K', 'soil_pH', 'temperature',
    'humidity', 'rainfall', 'sunlight_hours', 'last_crop', 'land_size'
]
data = pd.read_csv("Final.csv").fillna(method='ffill')
X = pd.get_dummies(data[features], columns=['last_crop'])
# Function to fetch historical sunlight and temperature data
async def fetch_historical_sunlight_temperature(latitude, longitude):
    past_years = 5
    end_year = datetime.now().year
    start_year = end_year - past_years

    url = f"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=ALLSKY_SFC_SW_DWN,T2M_MAX&community=AG&longitude={longitude}&latitude={latitude}&start={start_year}0101&end={end_year}1231&format=JSON"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                # Extract daily sunlight hours & max temperatures
                solar_radiation = data['properties']['parameter']['ALLSKY_SFC_SW_DWN'].values()
                max_temperatures = data['properties']['parameter']['T2M_MAX'].values()

                avg_sunlight_hours = np.mean(list(solar_radiation)) / 1.2  # Convert radiation to sunlight hours
                avg_temperature = np.mean(list(max_temperatures))

                return {
                    "avg_sunlight_hours": round(avg_sunlight_hours, 2),
                    "avg_temperature": round(avg_temperature, 2)
                }
            else:
                print("Error fetching historical sunlight data")
                return None

# Function to fetch weather forecast
async def fetch_weather_forecast(location, growth_days, user_input):
    latitude, longitude = get_coordinates(location)
    if latitude is None:
        return None  # Handle invalid locations

    # Fetch historical sunlight hours & temperature
    historical_data = await fetch_historical_sunlight_temperature(latitude, longitude)
    if historical_data:
        user_input.update(historical_data)
    else:
        print("Using default sunlight hours & temperature")
        user_input["avg_temperature"] = 25  # Default

    return user_input

# Function to adjust growth duration based on weather and terrain
async def adjust_growth_duration(crop, location, user_input):
    try:
        base_days = crops[crop]['growth_data']
    except KeyError:
        base_days = 120

    # Fetch weather data
    weather_data = await fetch_weather_forecast(location, base_days, user_input)
    if not weather_data:
        return base_days  # Return default if weather data is unavailable

    # Crop-specific sensitivity adjustments
    temp_deviation = 0
    if weather_data["avg_temperature"] < crops[crop]['temp_min']:
        temp_deviation = abs(crops[crop]['temp_min'] - weather_data["avg_temperature"])
    elif weather_data["avg_temperature"] > crops[crop]['temp_max']:
        temp_deviation = abs(crops[crop]['temp_max'] - weather_data["avg_temperature"])

    # Ensure avg_sunlight_hours is set before the calculation
    if weather_data.get("avg_sunlight_hours") is None:
        weather_data["avg_sunlight_hours"] = 0  # Default to 0 if no sunlight hours are available

    sun_hour_adjustment = abs(weather_data["avg_sunlight_hours"] - crops[crop]["sunlight_hours"]) / crops[crop]["sunlight_hours"] * crops[crop]["sun_factor"]

    # Adjust temperature factor: reduce impact further based on base days
    temp_adjustment_factor = min(1 + (temp_deviation / 500), 1.3)  # Max factor of 1.3
    sun_hour_adjustment = abs(1 - sun_hour_adjustment)
    sun_hour_adjustment = min(1 + sun_hour_adjustment, 1.3)

    if base_days > 365:  # If growth duration is more than a year, reduce the impact
        temp_adjustment_factor /= 2  # Reduce the temperature impact for longer growth cycles

    adjusted_days = base_days * crops[crop]["temp_factor"] * temp_adjustment_factor * sun_hour_adjustment
    return max(base_days, adjusted_days)

# Function to calculate fertilizer recommendations
def calculate_fertilizer(user_input, crop_data):
    recommendations = []
    land_size = user_input['land_size']

    # Nitrogen (Urea: 46% N)
    n_deficit = max(0, crop_data['optimal_N'] - user_input['N'])
    urea_kg = (n_deficit / 0.46) * land_size

    # Phosphorus (DAP: 46% P2O5 → 20% P)
    p_deficit = max(0, crop_data['optimal_P'] - user_input['P'])
    dap_kg = (p_deficit / 0.20) * land_size

    # Potassium (MOP: 60% K2O → 50% K)
    k_deficit = max(0, crop_data['optimal_K'] - user_input['K'])
    mop_kg = (k_deficit / 0.50) * land_size

    if urea_kg > 0:
        recommendations.append(f"Add {urea_kg:.2f} kg Urea")
    if dap_kg > 0:
        recommendations.append(f"Add {dap_kg:.2f} kg DAP")
    if mop_kg > 0:
        recommendations.append(f"Add {mop_kg:.2f} kg MOP")

    return recommendations

# Predefined crop pairs for hilly areas (to prevent soil erosion)
HILLY_CROP_PAIRS = [
    ("Cardamom", "Black Pepper"),
    ("Ginger", "Turmeric"),
    ("Cashewnut", "Coconut"),
    ("Arecanut", "Banana"),
    ("Sugarcane", "Sweet potato"),
    ("Tapioca", "Maize"),
    ("Ragi", "Horse-gram"),
    ("Sesamum", "Sunflower")
]

# Function to get hybrid recommendations based on terrain
def hybrid_recommendation(user_input, terrain):
    if terrain == "Hilly":
        # Return predefined crop pairs for hilly areas
        crop_pairs = HILLY_CROP_PAIRS
        recommendations = []

        for crop1, crop2 in crop_pairs:
            # Check if both crops exist in the data DataFrame
            if crop1 not in data['crop'].values or crop2 not in data['crop'].values:
                print(f"Skipping pair ({crop1}, {crop2}) because one or both crops are not in the dataset.")
                continue

            # Fetch data for both crops
            crop_data1 = data[data['crop'] == crop1].iloc[0]
            crop_data2 = data[data['crop'] == crop2].iloc[0]

            # Calculate expected profit for both crops (split land size equally)
            land_size1 = user_input['land_size'] / 2
            land_size2 = user_input['land_size'] / 2

            price1 = get_stable_price(user_input['location'], crop1)
            price2 = get_stable_price(user_input['location'], crop2)

            expected_profit1 = crop_data1['expected_yield'] * land_size1 * price1
            expected_profit2 = crop_data2['expected_yield'] * land_size2 * price2
            combined_profit = expected_profit1 + expected_profit2

            # Check if fertilizers are needed
            needs_fert1 = any([
                crop_data1['optimal_N'] > user_input['N'],
                crop_data1['optimal_P'] > user_input['P'],
                crop_data1['optimal_K'] > user_input['K']
            ])
            needs_fert2 = any([
                crop_data2['optimal_N'] > user_input['N'],
                crop_data2['optimal_P'] > user_input['P'],
                crop_data2['optimal_K'] > user_input['K']
            ])

            recommendations.append({
                'crop1': crop1,
                'crop2': crop2,
                'expected_profit': combined_profit,
                'needs_fertilizer1': needs_fert1,
                'needs_fertilizer2': needs_fert2,
                'price1': price1,
                'price2': price2
            })

        # Sort by combined profit
        recommendations.sort(key=lambda x: -x['expected_profit'])
        return recommendations[:3]  # Return top 3 pairs

    else:
        # For plain terrain, return individual crops (existing logic)
        user_df = pd.DataFrame([user_input])
        user_df = pd.get_dummies(user_df, columns=['last_crop'])
        for col in X.columns:
            if col not in user_df.columns:
                user_df[col] = 0
        user_df = scaler.transform(user_df[X.columns])

        xgb_probs = xgb_model.predict_proba(user_df)
        ann_probs = hybrid_model.predict([user_df, user_df])
        combined_probs = (xgb_probs + ann_probs) / 2

        top_10_idx = np.argsort(combined_probs[0])[-10:][::-1]
        recommendations = []

        for idx in top_10_idx:
            crop = le.inverse_transform([idx])[0]
            if crop not in data['crop'].values:
                print(f"Skipping crop {crop} because it is not in the dataset.")
                continue

            crop_data = data[data['crop'] == crop].iloc[0]
            needs_fert = any([
                crop_data['optimal_N'] > user_input['N'],
                crop_data['optimal_P'] > user_input['P'],
                crop_data['optimal_K'] > user_input['K']
            ])
            price = get_stable_price(user_input['location'], crop)
            recommendations.append({
                'crop': crop,
                'expected_profit': crop_data['expected_yield'] * user_input['land_size'] * price,
                'needs_fertilizer': needs_fert,
                'price': price
            })

        recommendations.sort(key=lambda x: (-x['expected_profit'], x['needs_fertilizer']))
        no_fert = [r for r in recommendations if not r['needs_fertilizer']]
        final_recs = [no_fert[0]] + [r for r in recommendations if r['needs_fertilizer']][:2] if no_fert else recommendations[:3]
        return final_recs

# Function to get enhanced recommendations
async def enhanced_recommendation(user_input, terrain):
    recommendations = hybrid_recommendation(user_input, terrain)  # Get recommendations based on terrain
    final_output = []

    if terrain == "Hilly":
        tasks = []
        for rec in recommendations:
            crop_data1 = data[data['crop'] == rec['crop1']].iloc[0]
            crop_data2 = data[data['crop'] == rec['crop2']].iloc[0]

            # Split land size equally
            land_size1 = user_input['land_size'] / 2
            land_size2 = user_input['land_size'] / 2

            # Fetch growth durations in parallel
            tasks.append(
                asyncio.gather(
                    adjust_growth_duration(rec['crop1'], user_input['location'], user_input),
                    adjust_growth_duration(rec['crop2'], user_input['location'], user_input)
                )
            )

        # Wait for all tasks to complete
        growth_durations = await asyncio.gather(*tasks)

        for idx, rec in enumerate(recommendations):
            growth_duration1, growth_duration2 = growth_durations[idx]
            crop_data1 = data[data['crop'] == rec['crop1']].iloc[0]
            crop_data2 = data[data['crop'] == rec['crop2']].iloc[0]

            fert_recommendation1 = calculate_fertilizer(user_input, crop_data1) if rec['needs_fertilizer1'] else []
            fert_recommendation2 = calculate_fertilizer(user_input, crop_data2) if rec['needs_fertilizer2'] else []

            final_output.append({
                'crop1': rec['crop1'],
                'crop2': rec['crop2'],
                'growth_duration1': f"{int(growth_duration1)} days",
                'growth_duration2': f"{int(growth_duration2)} days",
                'current_yield1': crop_data1['expected_yield'] * land_size1,
                'current_yield2': crop_data2['expected_yield'] * land_size2,
                'potential_yield1': crop_data1['expected_yield'] * (1.15 if rec['needs_fertilizer1'] else 1) * land_size1,
                'potential_yield2': crop_data2['expected_yield'] * (1.15 if rec['needs_fertilizer2'] else 1) * land_size2,
                'price_per_ton1': rec['price1'],
                'price_per_ton2': rec['price2'],
                'expected_profit': rec['expected_profit'],
                'fertilizer_recommendation1': fert_recommendation1,
                'fertilizer_recommendation2': fert_recommendation2
            })
    else:
        # Existing logic for plain terrain
        tasks = []
        for rec in recommendations:
            tasks.append(adjust_growth_duration(rec['crop'], user_input['location'], user_input))

        growth_durations = await asyncio.gather(*tasks)

        for idx, rec in enumerate(recommendations):
            growth_duration = growth_durations[idx]
            crop_data = data[data['crop'] == rec['crop']].iloc[0]
            fert_recommendation = calculate_fertilizer(user_input, crop_data) if rec['needs_fertilizer'] else []

            final_output.append({
            'crop': rec['crop'],
            'growth_duration': f"{int(growth_duration)} days",
            'current_yield': f"{crop_data['expected_yield'] * user_input['land_size']:.2f}",  # Format to 2 decimal places
            'potential_yield': f"{crop_data['expected_yield'] * (1.15 if rec['needs_fertilizer'] else 1) * user_input['land_size']:.2f}",  # Format to 2 decimal places
            'price_per_ton': f"{rec['price']:.2f}",  # Format to 2 decimal places
            'expected_profit': f"{rec['expected_profit']:.2f}",  # Format to 2 decimal places
            'fertilizer_recommendation': fert_recommendation
})


    return final_output

# # Function to run the recommendation system
# async def run_recommendation():
#     # Example user input
#     user_input = {
#         'soil_moisture': 45,  # Data by IoT
#         'N': 20,  # Data by IoT
#         'P': 15,  # Data by IoT
#         'K': 200,  # Data by IoT
#         'soil_pH': 6.2,  # Data by IoT
#         'temperature': 28,  # Data by IoT
#         'last_crop': 'wheat',  # Farmer Input
#         'land_size': 5,  # Farmer Input
#         'location': "Chennai,India"  # GPS
#     }

#     # Fetch weather data
#     weather_data = get_weather_data(user_input['location'])
#     if weather_data:
#         user_input.update(weather_data)

#     # Fetch current sunlight hours
#     sunlight_data = fetch_current_sunlight(user_input['location'])
#     if sunlight_data and "current_sunlight_hours" in sunlight_data:
#         user_input["sunlight_hours"] = sunlight_data["current_sunlight_hours"]

#     # Get elevation and classify terrain
#     lat, lon = get_coordinates(user_input['location'])
#     elevation = get_elevation(lat, lon)
#     terrain = classify_terrain(elevation)

#     # Get enhanced recommendations
#     final_recommendations = await enhanced_recommendation(user_input, terrain)

#     # Display results
#     if terrain == "Hilly":
#         print("\nTop 3 Profit-Maximizing Crop Pairs for Hilly Areas:")
#         for idx, rec in enumerate(final_recommendations, 1):
#             print(f"\n{idx}. {rec['crop1']} and {rec['crop2']}")
#             print(f"   - Growth duration of {rec['crop1']}: {rec['growth_duration1']}")
#             print(f"   - Growth duration of {rec['crop2']}: {rec['growth_duration2']}")
#             print(f"   - Combined Expected Revenue: ₹{rec['expected_profit']:,.2f}")

#             if rec['fertilizer_recommendation1']:
#                 print(f"   - Yield Boost Recommendations for {rec['crop1']}:")
#                 for fert in rec['fertilizer_recommendation1']:
#                     print(f"     • {fert}")
#             else:
#                 print(f"   - Soil nutrients optimal for {rec['crop1']} - no fertilizer needed")

#             if rec['fertilizer_recommendation2']:
#                 print(f"   - Yield Boost Recommendations for {rec['crop2']}:")
#                 for fert in rec['fertilizer_recommendation2']:
#                     print(f"     • {fert}")
#             else:
#                 print(f"   - Soil nutrients optimal for {rec['crop2']} - no fertilizer needed")
#     else:
#         print("\nTop 3 Profit-Maximizing Crops for Plain Areas:")
#         for idx, rec in enumerate(final_recommendations, 1):
#             print(f"\n{idx}. {rec['crop']}")
#             print(f"   - Growth duration: {rec['growth_duration']}")
#             print(f"   - Expected Revenue: ₹{rec['expected_profit']:,.2f}")

#             if rec['fertilizer_recommendation']:
#                 print("   - Yield Boost Recommendations:")
#                 for fert in rec['fertilizer_recommendation']:
#                     print(f"     • {fert}")
#             else:
#                 print("   - Soil nutrients optimal - no fertilizer needed")

# Run the recommendation system asynchronously


import requests
from geopy.geocoders import Nominatim

# Function to get location based on IP
def get_location():
    response = requests.get("https://ipinfo.io/json")
    data = response.json()
    if data["country"] == "IN":
        data["country"] = "India"
    location = f"{data['city']}, {data['region']}, {data['country']}"
    return location

# Function to get soil pH
def get_soil_ph(lat, lon):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&depth=0-5cm"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        return None  # Return None if the API request fails

    data = response.json()

    # Check if 'properties' and 'layers' exist in response
    if "properties" in data and "layers" in data["properties"]:
        for layer in data["properties"]["layers"]:
            if layer["name"] == "phh2o":  # Check if the layer is pH data
                for depth in layer["depths"]:
                    if depth["label"] == "0-5cm":  # Extract pH for topsoil
                        mean_ph = depth["values"].get("mean")
                        if mean_ph is not None:
                            return mean_ph / 10  # Convert pH from *10
                        else:
                            print("Soil pH data is missing in the API response.")
                            return None

    print("Soil pH data not available for this location.")
    return None

# Function to get coordinates
def get_coordinates(location):
    geolocator = Nominatim(user_agent="geoapi")
    geo_data = geolocator.geocode(location)
    if geo_data:
        return geo_data.latitude, geo_data.longitude
    return None, None

# Function to get weather data
def get_weather_data(location):
    latitude, longitude = get_coordinates(location)
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation&timezone=auto"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current_weather = data['current']

        weather_data = {
            'humidity': current_weather['relative_humidity_2m'],  # Humidity percentage
            'rainfall': current_weather.get('precipitation', 0),  # Rainfall in mm
            'temperature': current_weather.get('temperature_2m', 25)  # Temperature in Celsius
        }

        return weather_data
    else:
        print("Error fetching weather data")
        return None

def populate_user_input(user_provided_input):
    # Get location # GPS/calculated
    location = user_provided_input.get('location', get_location())
    print(f"Location: {location}")

    # Get coordinates
    lat, lon = get_coordinates(location)
    print(f"Coordinates: {lat}, {lon}")

    # Get weather data
    weather_data = get_weather_data(location)
    if not weather_data:
        weather_data = {
            'humidity': 60,  # Default humidity
            'rainfall': 0,   # Default rainfall
            'temperature': 28  # Default temperature
        }

    current_hour = datetime.now().hour  # Get current hour (24-hour format)
    if current_hour >= 22 or current_hour < 10:
        print("Market Close So taking pre-defined Values for crops")  # Directly use second API
    # Get soil pH
    soil_ph = get_soil_ph(lat, lon)
    if soil_ph is None:  # If soil pH is not available, use a default value
        soil_ph = 6.2
        print("Using default soil pH value: 6.2")

    # Populate user_input
    user_input = {
        'soil_moisture': user_provided_input.get('soil_moisture', 45),  # Data by IoT (default if not provided)
        'soil_pH': user_provided_input.get('soil_ph', soil_ph),   # Calculated or default
        'temperature': user_provided_input.get('temperature',weather_data['temperature']),  # From weather data
        'humidity':user_provided_input.get('land_size',weather_data['humidity']), # From weather data
        'rainfall': weather_data['rainfall'],  # From weather data
        'last_crop': user_provided_input.get('last_crop', 'wheat'),  # Farmer input (default if not provided)
        'land_size': user_provided_input.get('land_size', 5),  # Farmer input (default if not provided)
        # 'location': location,  # GPS/calculated
        'location':  user_provided_input.get('location',location),  # GPS/calculated
        'N': user_provided_input.get('N', 20),  # Nitrogen level (default if not provided)
        'P': user_provided_input.get('P', 15),  # Phosphorus level (default if not provided)
        'K': user_provided_input.get('K', 200)  # Potassium level (default if not provided)
    }

    return user_input


async def run_recommendation(user_provided_input):
    # Populate user_input with user-provided values and fetched data
    user_input = populate_user_input(user_provided_input)
    print("User Input:", user_input)

    # Get elevation and classify terrain
    lat, lon = get_coordinates(user_input['location'])
    elevation = get_elevation(lat, lon)
    terrain = classify_terrain(elevation)

    # Run the enhanced recommendation logic
    final_recommendations = await enhanced_recommendation(user_input, terrain)
    print("Final Recommendations:", final_recommendations)
    return final_recommendations

async def main():
    await run_recommendation({
    'location' : 'Punjab, India',
    'temperature' : 25,
    'humidity': 10,
    'soil_moisture': 50,  # Data by IoT
    'last_crop': 'wheat',  # Farmer input
    'land_size': 5       # Farmer input
})

asyncio.run(main()) 