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

def test_update_assembly_part_quantity(client):
    """Test the PUT /api/assemblies/<code>/parts/<pn>/quantity endpoint."""
    # First, get the assembly to check initial state
    response = client.get('/api/assemblies/ASM-CBL-001')
    assert response.status_code == 200
    initial_data = response.json
    assert 'assembly' in initial_data
    
    # Find the initial quantity for a part
    initial_parts = initial_data['assembly']['parts']
    assert len(initial_parts) > 0
    test_part = initial_parts[0]['part_number']
    initial_quantity = initial_parts[0]['quantity']
    
    # Update the quantity
    new_quantity = initial_quantity + 3
    response = client.put(
        f'/api/assemblies/ASM-CBL-001/parts/{test_part}/quantity',
        json={'quantity': new_quantity}
    )
    assert response.status_code == 200
    data = response.json
    assert 'assembly' in data
    assert 'message' in data
    assert f'Quantity updated to {new_quantity}' in data['message']
    
    # Verify the quantity was updated
    updated_parts = data['assembly']['parts']
    updated_part = next((p for p in updated_parts if p['part_number'] == test_part), None)
    assert updated_part is not None
    assert updated_part['quantity'] == new_quantity

def test_update_assembly_part_quantity_invalid_assembly(client):
    """Test updating quantity for non-existent assembly."""
    response = client.put(
        '/api/assemblies/INVALID-ASM/parts/ESP-MTR-001/quantity',
        json={'quantity': 5}
    )
    assert response.status_code == 404
    data = response.json
    assert 'error' in data

def test_update_assembly_part_quantity_invalid_part(client):
    """Test updating quantity for part not in assembly."""
    response = client.put(
        '/api/assemblies/ASM-CBL-001/parts/INVALID-PART/quantity',
        json={'quantity': 5}
    )
    assert response.status_code == 404
    data = response.json
    assert 'error' in data

def test_update_assembly_part_quantity_invalid_quantity(client):
    """Test updating quantity with invalid values."""
    # Missing quantity field
    response = client.put(
        '/api/assemblies/ASM-CBL-001/parts/ESP-CBL-001/quantity',
        json={}
    )
    assert response.status_code == 400
    
    # Non-integer quantity
    response = client.put(
        '/api/assemblies/ASM-CBL-001/parts/ESP-CBL-001/quantity',
        json={'quantity': 'not-a-number'}
    )
    assert response.status_code == 400
    
    # Zero quantity
    response = client.put(
        '/api/assemblies/ASM-CBL-001/parts/ESP-CBL-001/quantity',
        json={'quantity': 0}
    )
    assert response.status_code == 400
    
    # Negative quantity
    response = client.put(
        '/api/assemblies/ASM-CBL-001/parts/ESP-CBL-001/quantity',
        json={'quantity': -1}
    )
    assert response.status_code == 400