import datetime
import json
import requests

satellite_url = "http://localhost:3000"
create_endpoint = sensor_endpoint = "sensors"
ids_endpoint = "sensor-ids"


def now_timestamp():
    return datetime.datetime.now().isoformat()


class SatData:
    def __init__(self):
        self.all_sensor_data = {}

    def http_get(self, url):
        """Method for GETting JSON from the web"""
        # This could be improved using a session to mitigate the number of times the server closes the connection
        response = requests.get(url, timeout=1)
        return response

    def http_post(self, url, data):
        """Method for POSTing JSON to a web URL"""
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=data, headers=headers, timeout=1)
        return response

    def fetch_sensor_data(self, sensor_id):
        """Return the sensor object data from the satellite"""
        url = "{0}/{1}/{2}".format(satellite_url, sensor_endpoint, sensor_id)
        try:
            r = self.http_get(url)
            return r.status_code, r.json()
        except requests.exceptions.Timeout:
            return 408, "Timeout while fetching sensor data"
        except Exception as e:
            return 503, "Error while retrieving data: \n{0}".format(e)

    def retry_until_OK(self, function_to_retry, arg="", try_limit=0):
        """Call a function_to_retry with an argument "arg" if specified
        until the function returns 200 as its status code or reaches the try_limit.
        A try_limit of 0 will try forever"""
        try_count = 0
        status_code = 0
        json_data = {}
        while status_code != requests.codes.ok:
            if arg:
                status_code, json_data = function_to_retry(arg)
            else:
                status_code, json_data = function_to_retry()
            print("status_code: {0} | json_data {1}".format(status_code, json_data))
            try_count += 1
            if try_count == try_limit:
                return try_count, {"Message": "Try limit {0} reached".format(try_limit)}
        return try_count, json_data

    def fetch_sensors_list(self):
        """
        Communicate with the satellite to get the list of sensors
        """
        url = "{0}/{1}".format(satellite_url, ids_endpoint)
        try:
            r = self.http_get(url)
        except requests.exceptions.Timeout:
            return 408, "Timeout while fetching sensor list"
        return r.status_code, r.json()

    def update_cached_data(self):
        """
        Update the sensor data stored in memory for quick access
        """
        updated_sensor_data = []
        _, sensor_ids_list = self.retry_until_OK(self.fetch_sensors_list)
        print("GOT sensor_ids_list {0}".format(sensor_ids_list))
        for sensor_id in sensor_ids_list:
            _, json_data = self.retry_until_OK(self.fetch_sensor_data, arg=sensor_id)
            json_data.update(timestamp=now_timestamp())
            updated_sensor_data.append(json_data)
        return updated_sensor_data

    def create_sensor(self, frequency):
        """
        Create a sensor with a given frequency to collect data from the satellite
        """
        url = "{0}/{1}".format(satellite_url, create_endpoint)
        try:
            r = self.http_post(url, data={"frequency": frequency})
            return r.status_code
        except requests.exceptions.Timeout:
            return 408
