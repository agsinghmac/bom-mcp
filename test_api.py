# test_api.py
import pytest
from flask import Flask

from api import app  # Assuming your Flask app is in a file named 'api.py'

@pytest.fixture
def client():
    """A test fixture that creates a test client for the Flask application."""
    with app.test_client() as client:
        yield client

def test_get_esp(client):
    """Test the GET /api/esp/<id> endpoint."""
    response = client.get('/api/esp/ESP-001')
    assert response.status_code == 200
    data = response.json
    assert 'id' in data
    assert 'name' in data
    assert 'series' in data
    assert 'bom_weight' in data

def test_get_esp_bom(client):
    """Test the GET /api/esp/<id>/bom endpoint."""
    response = client.get('/api/esp/ESP-001/bom')
    assert response.status_code == 200
    data = response.json
    assert isinstance(data, list)
    for item in data:
        assert 'part_number' in item

def test_get_parts(client):
    """Test the GET /api/parts/<pn> endpoint."""
    response = client.get('/api/parts/ESP-MTR-001')
    assert response.status_code == 200
    data = response.json
    assert 'part_number' in data
    assert 'name' in data
    assert 'category' in data
    assert 'material' in data
    assert 'weight' in data
    assert 'critical' in data

def test_get_assemblies(client):
    """Test the GET /api/assemblies/<code> endpoint."""
    response = client.get('/api/assemblies/ASM-MTR-001')
    assert response.status_code == 200
    data = response.json
    assert 'code' in data
    assert 'name' in data
    assert 'bom_weight' in data
    assert isinstance(data['parts'], list)