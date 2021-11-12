from osu.osu_auth import OsuAuth


class Osu:
    def __init__(self):
        self.auth = OsuAuth()

    async def get_user_data(self, user_id: str):
        if user_id.isdigit():
            params = {"key": "id"}
        else:
            params = {"key": "username"}
        return await self.auth.get_api_v2(f"users/{user_id}", params=params)

