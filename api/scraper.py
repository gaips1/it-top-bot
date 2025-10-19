import asyncio
import aiohttp
import api.models as models

class TopAcademyScraper:
    def __init__(self, id, username, password, access_token=None):
        self.id = id
        self.username = username
        self.password = password
        self.base_url = 'https://msapi.top-academy.ru/api/v2/'
        self.session = None
        self.access_token = access_token

        self.login_payload = {
            "application_key": "6a56a5df2667e65aab73ce76d1dd737f7d1faef9c52e8b8c55ac75f565d8e8a6",
            "id_city": None,
            "password": self.password,
            "username": self.username
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def _login(self) -> bool:
        async with self.session.post(
            self.base_url + "auth/login",
            headers = {"accept": "application/json, text/plain, */*", "Referer": "https://journal.top-academy.ru/"},
            json = self.login_payload
        ) as login_response:
            login_data = await login_response.json()
            self.access_token = login_data.get('access_token') if isinstance(login_data, dict) else None

            if not self.access_token:
                return False
            
            print(f"Logged in as {self.username}")

            from database.models import users
            user = await users.get_user_by_id(self.id)
            if user:
                await user.update(access_token=self.access_token)
            
            return True
    
    async def get_user_info(self) -> models.StudentProfile | None:
        if not self.access_token:
            logged_in = await self._login()
            if not logged_in:
                return None

        headers = {
            "accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.access_token}",
            "Referer": "https://journal.top-academy.ru/"
        }

        async with self.session.get(
            self.base_url + "settings/user-info",
            headers = headers
        ) as user_response:
            if user_response.ok:
                user_data = await user_response.json()
                user_info = models.StudentProfile(**user_data)
                return user_info
        
        lgn = await self._login()
        if not lgn:
            return None
        
        info = await self.get_user_info()
        return info
    
    async def get_leaderboard(self, is_group) -> models.StudentRatingList | None:
        if not self.access_token:
            logged_in = await self._login()
            if not logged_in:
                return None

        headers = {
            "accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.access_token}",
            "Referer": "https://journal.top-academy.ru/"
        }

        async with self.session.get(
            self.base_url + "dashboard/progress/leader-group" if is_group else self.base_url + "dashboard/progress/leader-stream",
            headers = headers
        ) as lb_response:
            if lb_response.ok:
                lb_data = await lb_response.json()
                filtered_data = [item for item in lb_data if item.get('id') is not None]
                leaderboard = models.StudentRatingList(root=filtered_data)
                return leaderboard
        
        lgn = await self._login()
        if not lgn:
            return None
        
        lb = await self.get_leaderboard(is_group)
        return lb
    
    async def get_rewards(self) -> models.RewardsHistory | None:
        if not self.access_token:
            logged_in = await self._login()
            if not logged_in:
                return None

        headers = {
            "accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.access_token}",
            "Referer": "https://journal.top-academy.ru/"
        }

        async with self.session.get(
            self.base_url + "dashboard/progress/activity",
            headers = headers
        ) as rewards_response:
            if rewards_response.ok:
                rewards_data = await rewards_response.json()
                rewards = models.RewardsHistory(rewards_data)
                return rewards
        
        lgn = await self._login()
        if not lgn:
            return None
        
        rewards = await self.get_rewards()
        return rewards

if __name__ == '__main__':
    async def main():
        async with TopAcademyScraper("Marty_fx21", "8z69xdn1") as scraper:
            user_info = await scraper.get_user_info()
            print(user_info)

    asyncio.run(main())