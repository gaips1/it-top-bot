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
    
    async def get_leaderboard(self, is_group: bool) -> models.StudentRatingList | None:
        endpoint = "leader-group" if is_group else "leader-stream"
        url = f"{self.base_url}dashboard/progress/{endpoint}"

        for attempt in range(2):
            if (attempt == 0 and not self.access_token) or attempt == 1:
                if not await self._login():
                    break

            headers = {
                "accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.access_token}",
                "Referer": "https://journal.top-academy.ru/"
            }

            async with self.session.get(url, headers=headers) as response:
                if response.ok:
                    data = await response.json()
                    return models.StudentRatingList(root=[item for item in data if item.get('id') is not None])
        
        return None
    
    async def get_rewards(self) -> models.RewardsHistory | None:
        url = self.base_url + "dashboard/progress/activity"

        for attempt in range(2):
            if (attempt == 0 and not self.access_token) or attempt == 1:
                if not await self._login():
                    break

            headers = {
                "accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.access_token}",
                "Referer": "https://journal.top-academy.ru/"
            }

            async with self.session.get(url, headers=headers) as response:
                if response.ok:
                    data = await response.json()
                    return models.RewardsHistory(root=data)

        return None
    
    async def get_activity(self) -> models.ActivityList | None:
        url = self.base_url + "progress/operations/student-visits"

        for attempt in range(2):
            if (attempt == 0 and not self.access_token) or attempt == 1:
                if not await self._login():
                    break

            headers = {
                "accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.access_token}",
                "Referer": "https://journal.top-academy.ru/"
            }

            async with self.session.get(url, headers=headers) as response:
                if response.ok:
                    data = await response.json()
                    return models.ActivityList(root=data)

        return None
    
    async def get_homeworks(self, type: int) -> models.HomeworkList | None:
        url = self.base_url + f"homework/operations/list?page=1&status={type}&type=0&group_id=8"

        for attempt in range(2):
            if (attempt == 0 and not self.access_token) or attempt == 1:
                if not await self._login():
                    break

            headers = {
                "accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.access_token}",
                "Referer": "https://journal.top-academy.ru/"
            }

            async with self.session.get(url, headers=headers) as response:
                if response.ok:
                    data = await response.json()
                    return models.HomeworkList(root=data)

        return None