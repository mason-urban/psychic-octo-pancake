import pytest
import server
from unittest import mock
from server import app


def test_hello_world():
    response = app.test_client().get("/")
    assert b"Hello world!" == response.data


def test_all_sensors_empty():
    server.satellite_data.all_sensor_data = {}
    response = app.test_client().get("/all-sensors")
    assert response.json == {}


def test_all_sensors_populated():
    test_data = [
        {
            "frequency": 1246,
            "id": 1,
            "measurement": 46.634863434162725,
            "status": "ACTIVE",
            "timestamp": "2022-03-17T19:00:04.030424",
        },
    ]
    server.satellite_data.all_sensor_data = test_data
    response = app.test_client().get("/all-sensors")
    assert response.json == test_data


def test_create_sensor_empty_json_object():
    response = app.test_client().post("/create-sensor", json={})
    assert response.status_code == 400
    assert response.data == b'Field "frequency" must be a valid integer'


def test_create_sensor_invalid_frequency():
    response = app.test_client().post("/create-sensor", json={"frequency": "1245"})
    assert response.status_code == 400
    assert response.data == b'Field "frequency" must be a valid integer'


@mock.patch("sat_ops.SatData.create_sensor")
def test_create_sensor_valid_frequency(mock_create):
    mock_create.return_value = 200
    response = app.test_client().post("/create-sensor", json={"frequency": 1234})
    assert response.status_code == 200
