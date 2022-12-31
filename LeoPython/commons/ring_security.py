import base64
import json
import time
from datetime import datetime
from ring_doorbell import Auth, Ring


def utc2local (utc, timezone=None):
    epoch = time.mktime(utc.timetuple())
    offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp (epoch)
    return utc + offset


def display_token(token: dict) -> str:
    token_json_string = json.dumps(token, indent=4)
    print(token_json_string)
    print("Base64 Encoded:")
    token_b64_string = base64.b64encode(token_json_string.encode()).decode()
    print(token_b64_string)
    return token_b64_string


def authenticate_with_password(user_agent, username, password, code) -> Ring:
    auth = Auth(user_agent, None, display_token)
    auth.fetch_token(username, password, code)
    return Ring(auth)


def authenticate_with_b64_token(user_agent, token_b64_string: str) -> Ring:
    token = json.loads(base64.b64decode(token_b64_string.encode()).decode())
    return Ring(Auth(user_agent, token=token))


def prompt_and_authenticate_with_password() -> Ring:
    username = input("Enter ring.com username:")
    password = input("Enter ring.com password:")
    code = input("Enter ring.com verification code:")
    return Ring(authenticate_with_password("Leo", username, password, code))

def get_events(device, time_start, time_end, limit=None) -> list:
    events = []
    last_event_id = None
    last_event_time = time_end
    while last_event_time > time_start:
        history = device.history(limit=50, timezone=device.timezone, older_than=last_event_id)
        
        for event in history:
            last_event_id = event.get("id")
            event_time = event.get("created_at")
            if not event_time:
                continue
            last_event_time = event_time
            if event_time > time_start and event_time < time_end:
                events.append(event)
            if limit and len(events) > limit:
                return events
    return events


# Run this file as a Python script to obtain the ring.com token using username and password.
# Verification code is required to login using username and password.
# The verification code can be obtained from the ring.com website.
# Manage Account -> Account Verification -> Authorize a New Device
# Once authorized, this script will display the tokens.
if __name__ == "__main__":
    prompt_and_authenticate_with_password()
