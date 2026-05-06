from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Function to read our JSON database
def load_malls():
    with open('malls.json', 'r') as file:
        return json.load(file)

# ROUTE 1: The main API route that returns all malls
@app.route('/api/malls', methods=['GET'])
def get_malls():
    malls_data = load_malls()
    return jsonify(malls_data)

# ROUTE 2: Filter malls by maximum walking time (PROGRESS 3 UPDATE)
@app.route('/api/malls/walk/<int:max_time>', methods=['GET'])
def get_malls_by_walk_time(max_time):
    malls_data = load_malls()
    filtered_malls = []
    
    # Loop through and find malls where the walk time is LESS THAN or EQUAL to the requested time
    for mall in malls_data:
        if mall.get('walking_time_mins', 99) <= max_time:
            filtered_malls.append(mall)
            
    if len(filtered_malls) > 0:
        return jsonify(filtered_malls)
    
    return jsonify({"error": "No malls found within that walking distance"}), 404

# Start the server
if __name__ == '__main__':
    print("Starting TransitMall Mapper Backend...")
    app.run(debug=True)