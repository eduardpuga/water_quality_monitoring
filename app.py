from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# In-memory storage for demonstration purposes
water_quality_records = {}

# Swagger UI configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Water Quality Monitoring API"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Endpoint to add new water quality records
@app.route('/api/water-quality', methods=['POST'])
def add_record():
    data = request.get_json()
    if not data or not all(k in data for k in ("temperature", "pH", "conductivity", "location", "timestamp")):
        return jsonify({"error": "Invalid data format."}), 400
    
    record_id = len(water_quality_records) + 1
    water_quality_records[record_id] = data
    return jsonify({"id": record_id, "message": "Record successfully created."}), 201

# Endpoint to retrieve water quality records
@app.route('/api/water-quality', methods=['GET'])
def get_records():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location')

    filtered_records = [
        {"id": record_id, **record}
        for record_id, record in water_quality_records.items()
        if (not start_date or record["timestamp"] >= start_date) and
           (not end_date or record["timestamp"] <= end_date) and
           (not location or record["location"] == location)
    ]
    
    if not filtered_records:
        return jsonify({"error": "No records found."}), 404
    
    return jsonify(filtered_records), 200

# Endpoint to update existing records
@app.route('/api/water-quality/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    if record_id not in water_quality_records:
        return jsonify({"error": "Record not found."}), 404

    data = request.get_json()
    water_quality_records[record_id].update(data)
    return jsonify({"message": "Record successfully updated."}), 200

# Endpoint to delete records
@app.route('/api/water-quality/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    if record_id not in water_quality_records:
        return jsonify({"error": "Record not found."}), 404

    del water_quality_records[record_id]
    return jsonify({"message": "Record successfully deleted."}), 200

if __name__ == '__main__':
    app.run(debug=True)
