import urllib.request
import json
import uuid
import pytest

def get_token(email, password):
    req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', 
                                 data=json.dumps({'email': email, 'password': password}).encode('utf-8'), 
                                 headers={'Content-Type': 'application/json'})
    res = urllib.request.urlopen(req)
    return json.loads(res.read().decode())['access_token']


def post_hazard(token, description, location, filename, content_type, file_bytes):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    body = []
    
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="description"')
    body.append(b'')
    body.append(description.encode())
    
    body.append(f'--{boundary}'.encode())
    body.append(b'Content-Disposition: form-data; name="location"')
    body.append(b'')
    body.append(location.encode())
    
    if filename:
        body.append(f'--{boundary}'.encode())
        body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
        body.append(f'Content-Type: {content_type}'.encode())
        body.append(b'')
        body.append(file_bytes)
        
    body.append(f'--{boundary}--'.encode())
    body.append(b'')
    
    payload = b'\r\n'.join(body)
    
    req = urllib.request.Request(
        'http://localhost:8000/api/v1/hazard-reports',
        data=payload,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        },
        method='POST'
    )
    
    try:
        res = urllib.request.urlopen(req)
        return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())

@pytest.fixture(scope="module")
def worker_token():
    return get_token('worker@siteintel.com', 'WorkerSecurePass123!')

def test_valid_jpeg_upload(worker_token):
    status, _ = post_hazard(worker_token, "Exposed wiring near pump", "Zone A", "test.jpg", "image/jpeg", b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00' + b'A'*100)
    assert status == 201

def test_valid_png_upload(worker_token):
    status, _ = post_hazard(worker_token, "Chemical leak at storage", "Zone B", "test.png", "image/png", b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89' + b'B'*100)
    assert status == 201

def test_fake_magic_bytes_upload(worker_token):
    status, _ = post_hazard(worker_token, "Fake JPEG hazard report", "Zone C", "fake.jpg", "image/jpeg", b'THIS IS A FAKE TEXT FILE NAMED JPG')
    assert status == 400

def test_oversized_file_upload(worker_token):
    status, _ = post_hazard(worker_token, "Oversized image upload", "Zone D", "large.jpg", "image/jpeg", b'\xFF\xD8\xFF\xE0\x00\x10JFIF\x00' + b'0'*(5*1024*1024 + 1000))
    assert status == 400

def test_disallowed_exe_upload(worker_token):
    status, _ = post_hazard(worker_token, "Executable attachment test", "Zone E", "malicious.exe", "application/x-msdownload", b'MZ\x90\x00\x03\x00')
    assert status == 400
