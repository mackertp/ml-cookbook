
"""
Flask application to interface with the Tesla Fleet API.

@author: Preston Mackert
"""

# ------------------------------------------------------------------------------------- #
# libraries
# ------------------------------------------------------------------------------------- #

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, redirect, request, send_from_directory
import json, secrets, requests, urllib.parse, time, os


# ------------------------------------------------------------------------------------- #
# set app and key variables ~ change these to os.getenv()
# ------------------------------------------------------------------------------------- #

app = Flask(__name__)
ENV_FILE = Path(__file__).resolve().parents[2] / '.env'
load_dotenv(ENV_FILE)


def load_cached_tokens():
    raw = os.getenv('tesla_token_data', '')
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
    except Exception:
        return {}
    return {}


def upsert_env_value(key, value):
    """Replace an existing KEY=... line in .env, or append if missing."""
    line = f"{key}='{value}'"
    os.environ[key] = value
    if not ENV_FILE.exists():
        ENV_FILE.write_text(line + '\n', encoding='utf-8')
        return

    lines = ENV_FILE.read_text(encoding='utf-8').splitlines()
    updated = False
    new_lines = []
    for existing in lines:
        if existing.startswith(f'{key}='):
            if not updated:
                new_lines.append(line)
                updated = True
            # drop duplicate KEY= lines
            continue
        new_lines.append(existing)
    if not updated:
        if new_lines and new_lines[-1].strip():
            new_lines.append('')
        new_lines.append(line)
    ENV_FILE.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')


def save_cached_tokens(tokens):
    upsert_env_value('tesla_token_data', json.dumps(tokens))


def is_user_token(tokens):
    """Partner/client_credentials tokens cannot list a user's vehicles."""
    return bool(tokens.get('access_token') and tokens.get('refresh_token'))


class TeslaAPI:
    def __init__(self):
        self.client_id = os.getenv('tesla_client_key')
        self.client_secret = os.getenv('tesla_client_secret')
        self.redirect_uri = os.getenv('tesla_redirect_uri')
        self.scopes = os.getenv(
            'tesla_scopes',
            'openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds'
        )
        tokens = load_cached_tokens()
        self.tokens = tokens if is_user_token(tokens) else {}
        self.state = secrets.token_urlsafe(32)
        self.last_error = None

    def valid(self):
        return self.tokens and (int(time.time()) - self.tokens["obtained_at"] < self.tokens["expires_in"] - 60)

    def refresh(self):
        if not self.tokens.get('refresh_token'):
            self.tokens = {}
            self.last_error = 'Cached token is not a user OAuth token. Log in with Tesla again.'
            return False
        resp = requests.post("https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token", data={
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.tokens["refresh_token"]
        })
        if resp.status_code != 200:
            self.last_error = f'Token refresh failed: {resp.text}'
            self.tokens = {}
            return False
        r = resp.json()
        r["obtained_at"] = int(time.time())
        self.tokens.update(r)
        save_cached_tokens(self.tokens)
        self.last_error = None
        return True

    def api_get(self, path):
        if not self.valid() and not self.refresh():
            return None
        return requests.get(
            f"https://fleet-api.prd.na.vn.cloud.tesla.com{path}",
            headers={"Authorization": f"Bearer {self.tokens['access_token']}"}
        )

    def api_post(self, path):
        if not self.valid() and not self.refresh():
            return None
        return requests.post(
            f"https://fleet-api.prd.na.vn.cloud.tesla.com{path}",
            headers={"Authorization": f"Bearer {self.tokens['access_token']}"}
        )

    def get_vehicles(self):
        resp = self.api_get("/api/1/vehicles")
        if resp is None:
            return []
        try:
            payload = resp.json()
        except Exception:
            self.last_error = f'Non-JSON vehicles response ({resp.status_code}): {resp.text}'
            return []
        if resp.status_code != 200:
            self.last_error = f"Vehicles request failed ({resp.status_code}): {payload}"
            return []
        vehicles = payload.get('response') or []
        self.last_error = None
        return vehicles

    def get_vehicle_state(self, vid):
        vehicles = self.get_vehicles()
        vehicle = next((v for v in vehicles if str(v.get('id')) == str(vid)), None)
        return vehicle.get('state') if vehicle else None

    def wake_up_vehicle(self, vid):
        return self.api_post(f"/api/1/vehicles/{vid}/wake_up")

    def get_vehicle_data(self, vid):
        return self.api_get(f"/api/1/vehicles/{vid}/vehicle_data")

tesla_api = TeslaAPI()

def login_link():
    url = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/authorize?" + urllib.parse.urlencode({
        "client_id": tesla_api.client_id,
        "redirect_uri": tesla_api.redirect_uri,
        "response_type": "code",
        "scope": tesla_api.scopes,
        "state": tesla_api.state
    })
    return f"<a href='{url}'>Login with Tesla</a>"


@app.route("/")
def index():
    if not tesla_api.tokens:
        detail = f"<pre>{tesla_api.last_error}</pre>" if tesla_api.last_error else ""
        return f"<h1>Tesla Fleet</h1>{detail}<p>{login_link()}</p>"
    cars = tesla_api.get_vehicles()
    if not tesla_api.tokens:
        detail = f"<pre>{tesla_api.last_error}</pre>" if tesla_api.last_error else ""
        return f"<h1>Tesla Fleet</h1>{detail}<p>{login_link()}</p>"
    if tesla_api.last_error:
        return f"<h1>Your Vehicles</h1><pre>{tesla_api.last_error}</pre><p>{login_link()}</p>"
    if not cars:
        return (
            "<h1>Your Vehicles</h1>"
            "<p>No vehicles returned for this account.</p>"
            f"<p>{login_link()}</p>"
        )
    return "<h1>Your Vehicles</h1>" + "".join(
        f"<p><a href='/vehicle/{c['id']}'>{c.get('display_name') or 'Vehicle'} ({c.get('vin')})</a></p>"
        for c in cars
    )

@app.route("/auth/callback", strict_slashes=False)
# @app.route("/auth/callback/", strict_slashes=False)
def callback():
    if "error" in request.args:
        return f"<h1>Tesla OAuth Error</h1><pre>{dict(request.args)}</pre>", 400

    # Validate state parameter
    state = request.args.get("state")
    if state != tesla_api.state:
        return "<h1>Invalid state parameter (possible CSRF)</h1>", 400

    code = request.args.get("code")
    if not code:
        return f"<pre>{dict(request.args)}</pre>", 400

    resp = requests.post("https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token", data={
        "grant_type": "authorization_code",
        "client_id": tesla_api.client_id,
        "client_secret": tesla_api.client_secret,
        "code": code,
        "redirect_uri": tesla_api.redirect_uri
    })
    if resp.status_code != 200:
        return f"<h1>Token Exchange Failed</h1><pre>{resp.text}</pre>", 400
    token = resp.json()
    token["obtained_at"] = int(time.time())
    tesla_api.tokens.update(token)
    save_cached_tokens(tesla_api.tokens)
    return redirect("/")

@app.route("/vehicle/<vid>")
def vehicle(vid):
    import time
    # 1. Get vehicle state (without waking up)
    state = tesla_api.get_vehicle_state(vid)
    if state is None:
        detail = f"<pre>{tesla_api.last_error}</pre>" if tesla_api.last_error else ""
        return f"<h2>Vehicle not found in account.</h2>{detail}", 404
    # 2. If not online, try to wake up
    if state != 'online':
        wake_resp = tesla_api.wake_up_vehicle(vid)
        if wake_resp is None:
            return f"<h2>Wake up failed</h2><pre>{tesla_api.last_error}</pre>", 500
        try:
            wake_data = wake_resp.json()
        except Exception:
            return f"<h2>Wake up command failed (non-JSON response):</h2><pre>{wake_resp.text}</pre>", 500
        # 3. Poll for 'online' state, up to 5 times
        for attempt in range(5):
            time.sleep(2)
            poll_state = tesla_api.get_vehicle_state(vid)
            if poll_state == 'online':
                break
        else:
            return f"<h2>Vehicle did not wake up after several attempts.</h2><pre>{wake_data}</pre>", 500
    # 4. Fetch vehicle data
    data_resp = tesla_api.get_vehicle_data(vid)
    if data_resp is None:
        return f"<h2>Vehicle data failed</h2><pre>{tesla_api.last_error}</pre>", 500
    try:
        data = data_resp.json()
    except Exception:
        return f"<h2>Error parsing vehicle data response:</h2><pre>{data_resp.text}</pre>", 500

    # Pretty-print: flatten top-level keys and show as HTML table
    def render_dict(d, parent_key=""):
        rows = []
        for k, v in d.items():
            key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                rows.extend(render_dict(v, key))
            else:
                rows.append(f"<tr><td>{key}</td><td>{v}</td></tr>")
        return rows

    vehicle_info = data.get('response', {})
    table_rows = render_dict(vehicle_info)
    html = f'''
    <html>
    <head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f8f8f8; }}
        table {{ border-collapse: collapse; width: 80%; margin: 2em auto; background: #fff; }}
        th, td {{ border: 1px solid #ccc; padding: 8px 12px; }}
        th {{ background: #eee; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
        h2 {{ text-align: center; }}
    </style>
    </head>
    <body>
    <h2>Vehicle Data</h2>
    <table>
        <tr><th>Field</th><th>Value</th></tr>
        {''.join(table_rows)}
    </table>
    </body>
    </html>
    '''
    return html


@app.route('/.well-known/appspecific/<path:filename>')
def well_known(filename):
    return send_from_directory('.well-known/appspecific', filename)

if __name__ == "__main__":
    app.run(port=8080, debug=False)