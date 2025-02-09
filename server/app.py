from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MongoDB connection
client = MongoClient("mongodb+srv://nsakalkale:nsakalkale@cropwise.hslbw.mongodb.net/?retryWrites=true&w=majority&appName=CropWise")
db = client["CropWise"]
collection = db["data"]  # Change this to your actual collection name

@app.route('/data', methods=['GET'])
def get_data():
    # Fetch the most recent document (sorted by a timestamp field in descending order)
    data = collection.find_one({}, {"_id": 0}, sort=[("timestamp", -1)])  
    if data:
        print(data)
        return jsonify(data)
    return jsonify({"error": "No data found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
