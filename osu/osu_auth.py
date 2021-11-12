import json
import requests
import os
import asyncio
import time

class OsuAuth:
    def __init__(self):
        self._load_config()
        self.api_timer = time.time()

    def _load_config(self):
        with open(os.path.dirname(__file__) + "/../config.json") as f:
            data = json.load(f)['osu']
            self.address = data['address']
            self.apiv1_key = data['apiv1_key']
            self.client_id = data['client_id']
            self.client_secret = data['client_secret']

    def generate_access_token(self):
        r = requests.post('https://osu.ppy.sh/oauth/token',
                            headers=self._generate_headers(), json={
                                "grant_type": "client_credentials",
                                "client_id": self.client_id,
                                "client_secret": self.client_secret,
                                "scope": "public"
                            })

        data = json.loads(r.text)
        with open("authdata.json", "r") as jsonFile:
            authData = json.load(jsonFile)
        authData['token_type'] = data['token_type']
        authData['access_token'] = data['access_token']
        authData['expires_in'] = data['expires_in']
        with open("authdata.json", "w") as jsonFile:
            json.dump(authData, jsonFile)

    def _generate_headers(self):
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        with open("authdata.json", "r") as jsonFile:
            authData = json.load(jsonFile)
        headers['Authorization'] = 'Bearer ' + authData['access_token']

        return headers

    async def _get_api_v2(self, route):
        # Make sure the rate limit is not reached
        if (time.time() - self.api_timer) < 1:
            await asyncio.sleep(1 - (time.time() - self.api_timer))
        print("Time since last ping: ", "%.2f" %
            (time.time() - self.api_timer) + "s", end="\r")
        self.api_timer = time.time()
        try:
            r = requests.get(self.address + str(route),
                            headers=self._generate_headers())
        except(Exception):
            return {}
        if r.status_code == 200:
            dictionary = json.loads(r.text)
            return dictionary
        elif r.status_code == 401:
            self.generate_access_token()
            print("Resetting api key... expect bug.")
            return await self._get_api_v2(route)
        return {}