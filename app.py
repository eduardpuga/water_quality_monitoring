from flask import Flask, request, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
import logging

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
    """
    Add a new water quality record to the database.

    This endpoint accepts a JSON object with the following fields:
    - sensor_id (str): The ID of the sensor.
    - temperature (float): The temperature reading.
    - pH (float): The pH level.
    - conductivity (int): The conductivity value.
    - location (str): The location name.
    - timestamp (str): The time of the reading in ISO format.

    Returns:
        dict: A JSON response with the new record ID and a success message.
        HTTP Status Codes:
        - 201: Record successfully created.
        - 400: Invalid data format.
    """
    data = request.get_json()
    # Check if all required fields are present in the request
    if not data or not all(k in data for k in ("sensor_id", "temperature", "pH", "conductivity", "location", "timestamp")):
        return jsonify({"error": "Invalid data format."}), 400
    
    # Generate a new record ID
    record_id = len(water_quality_records) + 1
    # Add the new record to the in-memory storage
    try:
        water_quality_records[record_id] = data
        return jsonify({"id": record_id, "message": "Record successfully created."}), 201
    except Exception as e:
        logging.error(f"Error adding record: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Endpoint to retrieve water quality records
@app.route('/api/water-quality', methods=['GET'])
def get_records():
    """
    Retrieve water quality records from the database.

    This endpoint accepts the following query parameters:
    - start_date (str): The start date for filtering records in ISO format (optional).
    - end_date (str): The end date for filtering records in ISO format (optional).
    - location (str): The location name for filtering records (optional).

    Returns:
        list: A JSON array of filtered water quality records.
        HTTP Status Codes:
        - 200: Records successfully retrieved.
        - 404: No records found.
    """
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location')

    # Filter records based on query parameters
    filtered_records = [
        {"id": record_id, **record}
        for record_id, record in water_quality_records.items()
        if (not start_date or record["timestamp"] >= start_date) and
           (not end_date or record["timestamp"] <= end_date) and
           (not location or record["location"] == location)
    ]
    
    # Return an error if no records are found
    if not filtered_records:
        return jsonify({"error": "No records found."}), 404
    
    # Return the filtered records
    return jsonify(filtered_records), 200

# Endpoint to update existing records
@app.route('/api/water-quality/<int:record_id>', methods=['PUT'])
def update_record(record_id):
    """
    Update an existing water quality record in the database.

    This endpoint accepts a JSON object with one or more of the following fields:
    - temperature (float): The temperature reading (optional).
    - pH (float): The pH level (optional).
    - conductivity (int): The conductivity value (optional).
    - location (str): The location name (optional).
    - timestamp (str): The time of the reading in ISO format (optional).

    Args:
        record_id (int): The ID of the record to update.

    Returns:
        dict: A JSON response with a success message.
        HTTP Status Codes:
        - 200: Record successfully updated.
        - 400: Invalid data format.
        - 404: Record not found.
    """
    # Check if the record exists
    if record_id not in water_quality_records:
        return jsonify({"error": "Record not found."}), 404

    data = request.get_json()
    # Ensure that the request body is not empty and contains at least one updatable field
    if not data or not any(k in data for k in ("temperature", "pH", "conductivity", "location", "timestamp")):
        return jsonify({"error": "Invalid data format."}), 400
    
    # Update the record with new data
    water_quality_records[record_id].update(data)
    return jsonify({"message": "Record successfully updated."}), 200

# Endpoint to delete records
@app.route('/api/water-quality/<int:record_id>', methods=['DELETE'])
def delete_record(record_id):
    """
    Delete a water quality record from the database.

    Args:
        record_id (int): The ID of the record to delete.

    Returns:
        dict: A JSON response with a success message.
        HTTP Status Codes:
        - 200: Record successfully deleted.
        - 404: Record not found.
    """
    # Check if the record exists
    if record_id not in water_quality_records:
        return jsonify({"error": "Record not found."}), 404

    # Delete the record from the in-memory storage
    del water_quality_records[record_id]
    return jsonify({"message": "Record successfully deleted."}), 200

if __name__ == '__main__':
    app.run(debug=True)
