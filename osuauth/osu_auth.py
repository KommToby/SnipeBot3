import json
import requests
import os
import asyncio
import time


class OsuAuth:
    def __init__(self):
        self._load_config()
        self.api_timer = time.time()
        self._get_auth_token()

    def _load_config(self):
        with open(os.path.dirname(__file__) + "/../config.json") as f:
            data = json.load(f)['osu']
            self.address = data['address']
            self.apiv1_key = data['apiv1_key']
            self.client_id = data['client_id']
            self.client_secret = data['client_secret']

    def _get_auth_token(self) -> None:
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": "public",
        }
        r = requests.post("https://osu.ppy.sh/oauth/token", data=params)
        if r.status_code == 401:
            raise requests.RequestException("Invalid Credentials Given")
        response = r.json()
        self.refresh_time = time.time()
        self.token_type = response["token_type"]
        self.expires_in = response["expires_in"]
        self.access_token = response["access_token"]

    def auth_token_valid(self) -> bool:
        return time.time() < self.refresh_time + self.expires_in

    async def get_api_v2(self, url: str, params=None):
        if time.time() - self.api_timer < 0.05:
            await asyncio.sleep(0.05)
        print("Ping Time: ", "%.2f" % (time.time()-self.api_timer) + "s", end="\r")
        self.api_timer = time.time()
        if params is None:
            params = {}
        if not self.auth_token_valid():
            self._get_auth_token()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        r = requests.get(
            f"https://osu.ppy.sh/api/v2/{url}", headers=headers, params=params
        )
        self.api_timer = time.time()
        if r.status_code == 200:
            return r.json()
        else:
            return False

    async def get_user_data(self, user_id: str):
        return await self.get_api_v2(f"users/{user_id}")

    async def get_score_data(self, beatmap_id: str, user_id: str):
        return await self.get_api_v2(f"beatmaps/{beatmap_id}/scores/users/{user_id}")

    async def get_recent_plays(self, user_id: str):
        return await self.get_api_v2(f"users/{user_id}/scores/recent")

    async def get_user_scores(self, user_id: str):
        return await self.get_api_v2(f"users/{user_id}/scores/best")

    async def get_beatmap(self, beatmap_id: str):
        return await self.get_api_v2(f"beatmaps/{beatmap_id}")
