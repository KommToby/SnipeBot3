from osu.osu_auth import OsuAuth


class Osu:
    def __init__(self):
        self.auth = OsuAuth()

    async def get_user_data(self, user_id):
        return await self.auth._get_api_v2("/v2/users/" + str(user_id))
