import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import assignments
app = assignments.app

@pytest.fixture
def client():
    return app.test_client()

def test_healthz(client):
    response = client.get('/healthz', content_type='application/json')
    assert response.status_code == 200
    assert response.data == b''
    assert response.headers['cache-control'] == 'no-cache, no-store, must-revalidate'

def test_healthz_params(client):
    response = client.get('/healthz?args=1', content_type='application/json')
    assert response.status_code == 400
    assert response.data == b''
    assert response.headers['cache-control'] == 'no-cache, no-store, must-revalidate'

def test_healthz_body(client):
    response = client.get('/healthz', data='{ "name":"John"}', content_type='application/json')
    assert response.status_code == 400
    assert response.data == b''
    assert response.headers['cache-control'] == 'no-cache, no-store, must-revalidate'

def test_healthz_body_and_param(client):
    response = client.get('/healthz?args=10', data='{ "name":"John"}', content_type='application/json')
    assert response.status_code == 400
    assert response.data == b''
    assert response.headers['cache-control'] == 'no-cache, no-store, must-revalidate'

def test_healthx(client):
    response = client.get('/healthx', content_type='application/json')
    assert response.status_code == 404
    assert response.data == b''
    assert response.headers['cache-control'] == 'no-cache'

def test_healthz_with_post(client):
    response = client.post('/healthz', content_type='application/json')
    assert response.status_code == 405
    assert response.data == b''

def test_healthz_with_put(client):
    response = client.put('/healthz', content_type='application/json')
    assert response.status_code == 405
    assert response.data == b''

def test_healthz_with_delete(client):
    response = client.delete('/healthz', content_type='application/json')
    assert response.status_code == 405
    assert response.data == b''

def test_healthz_with_patch(client):
    response = client.patch('/healthz', content_type='application/json')
    assert response.status_code == 405
    assert response.data == b''