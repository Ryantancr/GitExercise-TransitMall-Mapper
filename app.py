from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================

def load_malls():
    with open('malls.json', 'r') as file:
        return json.load(file)

def save_malls(data):
    with open('malls.json', 'w') as file:
        json.dump(data, file, indent=4) 

def load_tips():
    if not os.path.exists('tips.json'):
        return []
    with open('tips.json', 'r') as file:
        return json.load(file)

def save_tips(data):
    with open('tips.json', 'w') as file:
        json.dump(data, file, indent=4)

# ==========================================
# ROUTE 1: GET ALL MALLS (Zhe Shern / Jie Liang Map)
# ==========================================
@app.route('/api/malls', methods=['GET'])
def get_malls():
    malls_data = load_malls()
    return jsonify(malls_data)

# ==========================================
# ROUTE 2: FILTER BY WALK TIME
# ==========================================
@app.route('/api/malls/walk/<int:max_time>', methods=['GET'])
def get_malls_by_walk_time(max_time):
    malls_data = load_malls()
    filtered_malls = [mall for mall in malls_data if mall.get('walking_time_mins', 99) <= max_time]
            
    if len(filtered_malls) > 0:
        return jsonify(filtered_malls)
    return jsonify({"error": "No malls found within that walking distance"}), 404

# ==========================================
# ROUTE 3: FILTER BY CATEGORY (Jie Liang's Buttons)
# ==========================================
@app.route('/api/malls/category/<string:cat_name>', methods=['GET'])
def get_malls_by_category(cat_name):
    malls_data = load_malls()
    filtered_malls = []
    
    for mall in malls_data:
        mall_categories = mall.get('categories', [])
        if cat_name in mall_categories:
            filtered_malls.append(mall)
            
    if len(filtered_malls) > 0:
        return jsonify(filtered_malls)
    return jsonify({"error": "No malls found for that category"}), 404

# ==========================================
# ROUTE 4: SUBMIT COMMUNITY TIP (POST)
# ==========================================
@app.route('/api/tips', methods=['POST'])
def submit_tip():
    new_tip_data = request.get_json()
    
    if not new_tip_data or 'tip_text' not in new_tip_data:
        return jsonify({"error": "Invalid data. 'tip_text' is required."}), 400

    tips = load_tips()
    new_entry = {
        "id": len(tips) + 1,
        "mall_name": new_tip_data.get('mall_name', 'General Tip'),
        "tip_text": new_tip_data['tip_text']
    }
    
    tips.append(new_entry)
    save_tips(tips)
    return jsonify({"message": "Tip saved successfully!", "tip": new_entry}), 201 

# ==========================================
# ROUTE 5 & 6: ADMIN CRUD LOGIC (POST & DELETE)
# ==========================================
@app.route('/api/malls', methods=['POST'])
def add_mall():
    new_mall = request.get_json()
    malls_data = load_malls()

    # Safely generate a new ID
    new_id = max(mall.get('id', 0) for mall in malls_data) + 1 if malls_data else 1
    new_mall['id'] = new_id

    malls_data.append(new_mall)
    save_malls(malls_data)
    return jsonify({"message": "Mall added successfully", "mall": new_mall}), 201

@app.route('/api/malls/<int:mall_id>', methods=['DELETE'])
def delete_mall(mall_id):
    malls_data = load_malls()
    # Keep only the malls that DO NOT match the deleted ID
    updated_malls = [mall for mall in malls_data if mall.get('id') != mall_id]

    if len(malls_data) == len(updated_malls):
        return jsonify({"error": "Mall not found"}), 404

    save_malls(updated_malls)
    return jsonify({"message": f"Mall {mall_id} deleted successfully"}), 200

# ==========================================
# ROUTE 7: UPDATE MALL (PUT) - The Missing Piece!
# ==========================================
@app.route('/api/malls/<int:mall_id>', methods=['PUT'])
def update_mall(mall_id):
    malls_data = load_malls()
    update_data = request.get_json()
    
    for mall in malls_data:
        if mall.get('id') == mall_id:
            # Update the specific mall's text data
            mall['mall_name'] = update_data.get('mall_name', mall.get('mall_name'))
            mall['station'] = update_data.get('station', mall.get('station'))
            mall['line'] = update_data.get('line', mall.get('line'))
            
            # Smart logic to handle nested or flat coordinates
            if 'coordinates' in mall:
                mall['coordinates']['lat'] = update_data.get('latitude', mall['coordinates'].get('lat'))
                mall['coordinates']['lon'] = update_data.get('longitude', mall['coordinates'].get('lon'))
            else:
                mall['latitude'] = update_data.get('latitude', mall.get('latitude'))
                mall['longitude'] = update_data.get('longitude', mall.get('longitude'))
                
            save_malls(malls_data)
            return jsonify({"message": "Mall successfully updated!", "data": mall}), 200
            
    return jsonify({"error": "Mall not found"}), 404

# ==========================================
# START THE SERVER (Dodging the Spam on Port 5001)
# ==========================================
if __name__ == '__main__':
    print("Starting TransitMall Mapper Backend on Port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)