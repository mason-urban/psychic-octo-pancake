from flask import Flask, make_response, request, jsonify
import sat_ops

app = Flask(__name__)
satellite_data = sat_ops.SatData()


@app.route("/")
def hello_world():
    return "Hello world!"


@app.route("/create-sensor", methods=["POST"])
def create_sensor():
    """
    Create a new sensor object in the satellite, by calling the /sensors endpoint.
    """
    try:
        frequency = request.json["frequency"]
    except KeyError:
        return 'Field "frequency" must be a valid integer', 400

    if not isinstance(frequency, int):
        return 'Field "frequency" must be a valid integer', 400

    status_code = satellite_data.create_sensor(frequency)
    return jsonify(status_code)


@app.route("/poll")
def poll():
    """
    Update local cache with the latest sensor data from all sensors.
    """
    try:
        satellite_data.all_sensor_data = satellite_data.update_cached_data()
        return "OK", 200
    except ValueError:
        msg = "Unable to return sensor data, no JSON data found for sensors in all sensors"
        return msg, 404
    return jsonify(500)


@app.route("/all-sensors")
def all_sensors():
    """
    Return the latest cached data for all sensors, including timestamps.
    """
    return jsonify(satellite_data.all_sensor_data)


if __name__ == "__main__":
    satellite_data.update_cached_data()
