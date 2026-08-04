import urllib.request
import json
import time

def get_auth_token():
    for _ in range(5):
        try:
            req = urllib.request.Request(
                'http://localhost:8000/api/v1/auth/login',
                data=json.dumps({'email': 'admin@siteintel.com', 'password': 'AdminSecurePass123!'}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            res = urllib.request.urlopen(req)
            return json.loads(res.read().decode())['access_token']
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(2)
            else:
                raise e
    raise Exception("Rate limited")

def test_get_deliveries_escalations_proof():
    token = get_auth_token()
    req1 = urllib.request.Request(
        'http://localhost:8000/api/v1/deliveries/escalations',
        headers={'Authorization': f'Bearer {token}'}
    )
    res1 = urllib.request.urlopen(req1)
    assert res1.status == 200

def test_post_violations_process_video_proof():
    token = get_auth_token()
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    with open('storage/demo_clips/demo_compliant.mp4', 'rb') as f:
        file_bytes = f.read()

    body = [
        f'--{boundary}'.encode(),
        b'Content-Disposition: form-data; name="file"; filename="demo_compliant.mp4"',
        b'Content-Type: video/mp4',
        b'',
        file_bytes,
        f'--{boundary}--'.encode(),
        b''
    ]
    payload = b'\r\n'.join(body)

    req2 = urllib.request.Request(
        'http://localhost:8000/api/v1/violations/process-video',
        data=payload,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': f'multipart/form-data; boundary={boundary}'
        },
        method='POST'
    )
    res2 = urllib.request.urlopen(req2)
    assert res2.status == 200
