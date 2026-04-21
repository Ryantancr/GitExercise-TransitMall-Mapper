from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Function to read our JSON database
def load_malls():
    with open('malls.json', 'r') as file:
        return json.load(file)

# The API route that the frontend map will call
@app.route('/api/malls', methods=['GET'])
def get_malls():
    malls_data = load_malls()
    return jsonify(malls_data)

# Start the server
if __name__ == '__main__':
    print("Starting TransitMall Mapper Backend...")
    app.run(debug=True)