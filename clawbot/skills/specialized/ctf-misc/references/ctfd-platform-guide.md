# CTFd CTF challenge guidance

## CTFd API CTF challenge guidance

```python
import requests

CTFD_URL = "https://ctf.example.com"
session = requests.Session()

def login(username, password):
    """CTF challenge guidance CTFd"""
    r = session.post(f"{CTFD_URL}/login", data={
        "name": username,
        "password": password,
    })
    return r

def get_challenges():
    """CTF challenge guidance"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges")
    return r.json()

def get_challenge_detail(chal_id):
    """CTF challenge guidance"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges/{chal_id}")
    return r.json()

def get_challenge_files(chal_id):
    """CTF challenge guidance"""
    r = session.get(f"{CTFD_URL}/api/v1/challenges/{chal_id}/files")
    return r.json()

def download_file(file_id):
    """CTF challenge guidance"""
    r = session.get(f"{CTFD_URL}/api/v1/files/{file_id}")
    return r.content

def submit_flag(flag):
    """CTF challenge guidance flag"""
    r = session.post(f"{CTFD_URL}/api/v1/challenges/attempt", json={
        "challenge_id": chal_id,
        "submission": flag,
    })
    return r.json()

def get_scoreboard():
    """CTF challenge guidance"""
    r = session.get(f"{CTFD_URL}/api/v1/scoreboard")
    return r.json()

def get_user_info():
    """CTF challenge guidance"""
    r = session.get(f"{CTFD_URL}/api/v1/users/me")
    return r.json()
```

## CTF challenge guidance

```python
def detect_platform(url):
    """CTF challenge guidance CTF CTF challenge guidance"""
    # CTFd
    r = requests.get(f"{url}/login")
    if 'ctfd' in r.text.lower() or 'csrf_token' in r.text:
        return "CTFd"

    # RBCG / CTFdLight
    if '/static/core' in r.text:
        return "RBCG"

    # HCTF / others
    return "Unknown"
```

## CTF challenge guidance CTFd API

```
GET  /api/v1/challenges          # CTF challenge guidance
GET  /api/v1/challenges/{id}     # CTF challenge guidance
GET  /api/v1/challenges/{id}/files # CTF challenge guidance
POST /api/v1/challenges/attempt  # CTF challenge guidance flag
GET  /api/v1/scoreboard          # CTF challenge guidance
GET  /api/v1/users/me            # CTF challenge guidance
GET  /api/v1/notifications       # CTF challenge guidance
```

## CTF challenge guidance

```python
def download_all_files(url, output_dir):
    """CTF challenge guidance"""
    import os
    os.makedirs(output_dir, exist_ok=True)

    challenges = get_challenges()['data']
    for chal in challenges:
        chal_id = chal['id']
        try:
            files = get_challenge_files(chal_id)['data']
            for f in files:
                filename = f['filename']
                content = download_file(f['id'])
                with open(os.path.join(output_dir, filename), 'wb') as out:
                    out.write(content)
                print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download challenge {chal_id}: {e}")
```

## CTF challenge guidance

```python
def auto_solve(url, username, password, solve_func):
    """CTF challenge guidance

    solve_func(challenge_data) -> flag
    """
    session = requests.Session()
    login(username, password)

    challenges = get_challenges()['data']
    for chal in challenges:
        chal_id = chal['id']
        detail = get_challenge_detail(chal_id)['data']
        files = get_challenge_files(chal_id)['data']

        print(f"Solving: {detail['name']}")
        flag = solve_func(detail, files)

        if flag:
            result = submit_flag(flag)
            if result.get('data', {}).get('status') == 'correct':
                print(f"[✓] {detail['name']}: {flag}")
            else:
                print(f"[✗] {detail['name']}: Wrong flag")
        else:
            print(f"[-] {detail['name']}: No solve function")
```
