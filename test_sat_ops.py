import json
import pytest
import requests
import unittest
from unittest import mock

import sat_ops

sensor_ids_test_data = [1, 2, 3, 4]
sensors_1_test_data = {
    "id": 1,
    "frequency": 1246,
    "status": "ACTIVE",
    "measurement": 46.634863434162725,
}
sensors_2_test_data = {
    "id": 2,
    "frequency": 1247,
    "status": "ACTIVE",
    "measurement": 47.634863434162725,
}
sensors_3_test_data = {
    "id": 3,
    "frequency": 1248,
    "status": "ACTIVE",
    "measurement": 48.634863434162725,
}
sensors_4_test_data = {
    "id": 4,
    "frequency": 1249,
    "status": "ACTIVE",
    "measurement": 49.634863434162725,
}
fake_timestamp = "2022-03-17T19:00:04.030424"


all_cached_test_data = [
    {
        "frequency": 1246,
        "id": 1,
        "measurement": 46.634863434162725,
        "status": "ACTIVE",
        "timestamp": "2022-03-17T19:00:04.030424",
    },
    {
        "frequency": 1247,
        "id": 2,
        "measurement": 47.634863434162725,
        "status": "ACTIVE",
        "timestamp": "2022-03-17T19:00:04.030424",
    },
    {
        "frequency": 1248,
        "id": 3,
        "measurement": 48.634863434162725,
        "status": "ACTIVE",
        "timestamp": "2022-03-17T19:00:04.030424",
    },
    {
        "frequency": 1249,
        "id": 4,
        "measurement": 49.634863434162725,
        "status": "ACTIVE",
        "timestamp": "2022-03-17T19:00:04.030424",
    },
]


def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def status_code(self):
            return self.status_code

        def content(self):
            pass

    if args[0] == "{0}/{1}/{2}".format(
        sat_ops.satellite_url, sat_ops.sensor_endpoint, "1"
    ):
        return MockResponse(sensors_1_test_data, requests.codes.ok)
    if args[0] == "{0}/{1}/{2}".format(
        sat_ops.satellite_url, sat_ops.sensor_endpoint, "2"
    ):
        return MockResponse(sensors_2_test_data, 200)
    if args[0] == "{0}/{1}/{2}".format(
        sat_ops.satellite_url, sat_ops.sensor_endpoint, "3"
    ):
        return MockResponse(sensors_3_test_data, 200)
    if args[0] == "{0}/{1}/{2}".format(
        sat_ops.satellite_url, sat_ops.sensor_endpoint, "4"
    ):
        return MockResponse(sensors_4_test_data, 200)
    elif args[0] == "{0}/{1}/{2}".format(
        sat_ops.satellite_url, sat_ops.sensor_endpoint, "5"
    ):
        return MockResponse({}, 400)
    elif args[0] == "{0}/{1}".format(sat_ops.satellite_url, sat_ops.ids_endpoint):
        return MockResponse(sensor_ids_test_data, 200)

    return MockResponse(None, 404)


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def status_code(self):
            return self.status_code

    if args[0] == "{0}/{1}".format(sat_ops.satellite_url, sat_ops.create_endpoint):
        return MockResponse("OK", 200)
    return MockResponse(None, 404)


class TestSatData(unittest.TestCase):
    def setup_method(self, method):
        self.SatData = sat_ops.SatData()

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_fetch_sensor_data(self, mock_get):
        status_code, json_response = self.SatData.fetch_sensor_data(1)
        assert status_code == 200
        assert json_response == sensors_1_test_data

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_poll_sensor_data_200(self, mock_get):
        try_count, test_sensor_data = self.SatData.retry_until_OK(
            function_to_retry=self.SatData.fetch_sensor_data, arg=1, try_limit=5
        )
        assert try_count == 1
        assert test_sensor_data == sensors_1_test_data

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_retry_until_OK_retries_on_400(self, mock_get):
        try_count, test_sensor_data = self.SatData.retry_until_OK(
            function_to_retry=self.SatData.fetch_sensor_data, arg=5, try_limit=5
        )
        assert try_count == 5
        assert test_sensor_data == {"Message": "Try limit 5 reached"}

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_retry_until_OK_fetch_sensors_list(self, mock_get):
        try_count, test_sensor_ids = self.SatData.retry_until_OK(
            function_to_retry=self.SatData.fetch_sensors_list, try_limit=2
        )
        assert try_count == 1
        assert test_sensor_ids == sensor_ids_test_data

    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_get_sensors_list(self, mock_get):
        self.SatData.all_sensors = sensor_ids_test_data
        test_status_code, test_response = self.SatData.fetch_sensors_list()
        assert test_status_code == 200
        assert test_response == sensor_ids_test_data

    @mock.patch("sat_ops.now_timestamp")
    @mock.patch("requests.get", side_effect=mocked_requests_get)
    def test_update_cached_data(self, mock_get, mock_timestamp):
        mock_timestamp.return_value = fake_timestamp
        actual_data = self.SatData.update_cached_data()
        assert all_cached_test_data == actual_data

    @mock.patch("requests.post", side_effect=mocked_requests_post)
    def test_create_sensor(self, mock_post):
        test_status_code = self.SatData.create_sensor(frequency=1234)
        assert test_status_code == 200
