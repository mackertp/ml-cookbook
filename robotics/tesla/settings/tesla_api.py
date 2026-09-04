"""
Tesla Fleet API helper.

Reference: https://developer.tesla.com/docs/fleet-api/getting-started/what-is-fleet-api
Video: https://www.youtube.com/watch?v=GX3pV4udQfs

@author Preston Mackert
"""

# ------------------------------------------------------------------------------------------------------- #
# libraries
# ------------------------------------------------------------------------------------------------------- #

from __future__ import annotations

import os
import json
import time
import secrets
import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[3] / '.env'
BASE_API = 'https://fleet-api.prd.na.vn.cloud.tesla.com'
load_dotenv(ENV_FILE)

# ------------------------------------------------------------------------------------------------------- #
# interface for the fleet api
# ------------------------------------------------------------------------------------------------------- #

class Tesla:
    """
    Configure the API connection to access Fleet features.
    """
    def __init__(self, id=None):
        """
        Set key support variables used for requests, initiate functions to automatically set and manage 
        tokens. If vehicle id is set, collect VIN #. 
        """
        self.domain = 'manned-sprinkler-reversion.ngrok-free.dev'
        self.client_id = os.getenv('tesla_client_key')
        self.client_secret = os.getenv('tesla_client_secret')
        self.redirect_uri = os.getenv('tesla_redirect_uri')
        self.scopes = 'openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds'
        self.audience = 'https://fleet-api.prd.na.vn.cloud.tesla.com'
        self.token_data = self.load_cached_tokens()
        self.access_token = self.token_data.get('access_token', '')
        self.energy_site_id = None
        self.vehicle_id = id
        self.vin = None
        self.state = secrets.token_urlsafe(32)
        self._set_energy_site_id()
        self._set_vin_from_vehicle_id()

    def load_cached_tokens(self, key='tesla_token_data'):
        raw = os.getenv(key, '')
        if not raw:
            return {}
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data
        except Exception:
            return {}
        return {}

    def _upsert_env_value(self, key, value):
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
                continue
            new_lines.append(existing)
        if not updated:
            if new_lines and new_lines[-1].strip():
                new_lines.append('')
            new_lines.append(line)
        ENV_FILE.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')

    def save_cached_tokens(self, key='tesla_token_data'):
        if self.token_data:
            self._upsert_env_value(key, json.dumps(self.token_data))

    # --------------------------------------------------------------------------------------------------- #
    # register partner application / token management
    # --------------------------------------------------------------------------------------------------- #

    def obtain_access_token(self, token_endpoint='https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token'):
        """
        Partner/client_credentials token for registration only.
        Stored separately so it does not overwrite the user OAuth token used by the Flask app.
        """
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': self.scopes,
            'audience': self.audience,
        }
        response = requests.post(token_endpoint, data=data)
        partner_token = response.json()
        partner_token['obtained_at'] = int(time.time())
        self._upsert_env_value('tesla_partner_token_data', json.dumps(partner_token))
        return response, partner_token

    def ensure_access_token(self):
        if self.valid():
            return self.access_token

        if self.token_data.get('refresh_token'):
            response = requests.post(
                'https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token',
                data={
                    'grant_type': 'refresh_token',
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'refresh_token': self.token_data['refresh_token'],
                },
            )
            if response.ok:
                refreshed = response.json()
                self.token_data.update(refreshed)
                self.token_data['obtained_at'] = int(time.time())
                self.access_token = self.token_data.get('access_token', '')
                self.save_cached_tokens()
                return self.access_token

        return self.access_token

    def initialize_partner_access(self, partner_endpoint='/api/1/partner_accounts'):
        """
        Obtain a partner token and register the app domain. Does not replace user OAuth tokens.
        """
        response, partner_token = self.obtain_access_token()
        partner_access = partner_token.get('access_token', '')
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + partner_access,
        }
        data = {'domain': self.domain}
        return requests.post(
            self.audience + partner_endpoint, headers=headers, json=data
        )

    def register_partner_app(self, partner_endpoint='/api/1/partner_accounts'):
        """
        Backward-compatible wrapper for partner registration.
        """
        return self.initialize_partner_access(partner_endpoint)

    # --------------------------------------------------------------------------------------------------- #
    # automatic class functions
    # --------------------------------------------------------------------------------------------------- #

    def _set_energy_site_id(self):
        """
        Discover the first available energy site id for the authenticated account and store it on the class.
        """
        self.ensure_access_token()
        if not self.access_token:
            return

        endpoint = f"{BASE_API}/api/1/products"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(endpoint, headers=headers)
        if not response.ok:
            return

        payload = response.json().get('response', [])
        for item in payload:
            if item.get('resource_type') in {'energy_site', 'site'}:
                site_id = item.get('id') or item.get('energy_site_id')
                if site_id:
                    self.energy_site_id = site_id
                    break

    def _set_vin_from_vehicle_id(self):
        """
        Resolve the VIN for the configured vehicle ID from the vehicles response.
        """
        if not self.vehicle_id:
            return

        vehicles_df = self.get_vehicles()
        if vehicles_df.empty:
            self.vin = None
            return

        id_column = 'id' if 'id' in vehicles_df.columns else ('ID' if 'ID' in vehicles_df.columns else None)
        if id_column is None or 'vin' not in vehicles_df.columns:
            self.vin = None
            return

        match = vehicles_df[vehicles_df[id_column] == self.vehicle_id]
        if match.empty:
            raise ValueError(f'No vehicle found with id {self.vehicle_id}')

        self.vin = match['vin'].iloc[0]

    # --------------------------------------------------------------------------------------------------- #
    # validate access token / refresh helpers
    # --------------------------------------------------------------------------------------------------- #

    def valid(self):
        """ checks to see if access token is still valid """
        if not self.access_token or not self.token_data:
            return False
        expires_in = self.token_data.get('expires_in', 0)
        obtained_at = self.token_data.get('obtained_at', 0)
        return bool(expires_in) and (int(time.time()) - obtained_at < expires_in - 60)

    # --------------------------------------------------------------------------------------------------- #
    # vehicle api endpoints
    # --------------------------------------------------------------------------------------------------- #

    def get_vehicles(self, endpoint=BASE_API+'/api/1/vehicles'):
        """
        utility to list all vehicle info
        """
        self.ensure_access_token()
        if not self.access_token:
            raise ValueError('No access token was found. Complete the Tesla login flow again.')

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(endpoint, headers=headers)
        vehicles = response.json().get('response', [])
        return pd.DataFrame(vehicles)

    def _resolve_vehicle_id(self, vehicle_id=None):
        if vehicle_id is not None:
            return vehicle_id
        if self.vehicle_id is not None:
            return self.vehicle_id

        vehicles_df = self.get_vehicles()
        if vehicles_df.empty:
            raise ValueError('No vehicles were found for this account.')

        if 'id' in vehicles_df.columns:
            return vehicles_df['id'].iloc[0]
        if 'ID' in vehicles_df.columns:
            return vehicles_df['ID'].iloc[0]
        raise ValueError('No vehicle id column was found in the vehicles response.')

    def _get_vehicle_endpoint(self, path, vehicle_id=None, params=None, default=None, raise_for_status=True):
        self.ensure_access_token()
        if not self.access_token:
            raise ValueError('No access token was found. Complete the Tesla login flow again.')

        resolved_vehicle_id = self._resolve_vehicle_id(vehicle_id)
        headers = {'Authorization': f'Bearer {self.access_token}'}
        endpoint = f"{BASE_API}{path.format(vehicle_id=resolved_vehicle_id)}"
        try:
            response = requests.get(endpoint, params=params or {}, headers=headers, timeout=15)
            if raise_for_status:
                response.raise_for_status()
            return response.json() if response.ok else default
        except (requests.RequestException, ValueError, KeyError):
            return default

    def get_vehicle_info(self, vehicle_id=None, params=None):
        return self._get_vehicle_endpoint('/api/1/vehicles/{vehicle_id}', vehicle_id=vehicle_id, params=params, default={})

    def get_vehicle_specs(self, vehicle_id=None, params=None):
        payload = self._get_vehicle_endpoint(
            '/api/1/vehicles/{vehicle_id}/vehicle_data',
            vehicle_id=vehicle_id,
            params=params,
            default={},
            raise_for_status=False,
        )
        response = payload.get('response', {}) if isinstance(payload, dict) else {}
        if isinstance(response, dict):
            return response
        return {}

    def get_drivers(self, vehicle_id=None, params=None):
        return self._get_vehicle_endpoint('/api/1/vehicles/{vehicle_id}/drivers', vehicle_id=vehicle_id, params=params)

    def get_vehicle_data(self, vehicle_id=None, params=None):
        payload = self._get_vehicle_endpoint(
            '/api/1/vehicles/{vehicle_id}/vehicle_data',
            vehicle_id=vehicle_id,
            params=params,
            default={},
            raise_for_status=False,
        )
        if isinstance(payload, dict):
            return payload.get('response', payload)
        return {}

    def get_charge_history(self, endpoint=BASE_API+'/api/1/dx/charging/history', page_size=25, max_pages=None):
        """
        Return all charging-history rows for the authenticated vehicle account as a DataFrame.
        The API defaults to returning a page of results, so this method iterates through the
        history endpoint until it has collected all available rows or reaches the page limit.
        """
        self.ensure_access_token()
        if not self.access_token:
            raise ValueError('No access token was found. Complete the Tesla login flow again.')

        headers = {'Authorization': f'Bearer {self.access_token}'}
        page = 0
        frames = []
        total_results = None

        while True:
            params = {'limit': page_size, 'offset': page * page_size}
            response = requests.get(endpoint, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

            if isinstance(payload, dict):
                # Tesla responses may wrap charge history under a response object.
                if isinstance(payload.get('response'), dict):
                    payload = payload['response']
                elif isinstance(payload.get('response'), list):
                    payload = {'data': payload['response']}

            data = payload.get('data', []) if isinstance(payload, dict) else payload
            if isinstance(data, dict):
                data = data.get('data', [])

            if not isinstance(data, list) or not data:
                break

            frames.append(pd.DataFrame(data))
            total_results = payload.get('totalResults', total_results) if isinstance(payload, dict) else total_results
            page += 1

            if max_pages is not None and page >= max_pages:
                break

            if total_results is not None and len(frames) * page_size >= int(total_results):
                break

        if not frames:
            return pd.DataFrame()

        return pd.concat(frames, ignore_index=True)
        