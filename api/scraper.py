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
        self.default_headers = {
            "accept": "application/json, text/plain, */*",
            "Authorization": f"Bearer {self.access_token}",
            "Referer": "https://journal.top-academy.ru/"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def _login(self) -> bool:
        async with self.session.post(
            f"{self.base_url}auth/login",
            headers=self.default_headers,
            json=self.login_payload,
        ) as response:
            if response.status != 200:
                return False

            try:
                data = await response.json()
            except aiohttp.ContentTypeError:
                print(1)
                return False

            self.access_token = data.get("access_token")
            if not self.access_token:
                return False

            print(f"✅ Logged in as {self.username}")

            try:
                from database.models import users
                user = await users.get_user_by_id(self.id)
                if user:
                    await user.update(access_token=self.access_token)
            except Exception as e:
                print(f"couldnt update user token: {e}")

            return True
        
    async def _request(self, method: str, endpoint: str, *, json=None, retry: bool = True):
        if not self.session:
            self.session = aiohttp.ClientSession()

        if not self.access_token and not await self._login():
            return None

        url = self.base_url + endpoint

        try:
            async with self.session.request(method.upper(), url, headers=self.default_headers, json=json) as response:
                if response.status == 401 and retry:
                    if await self._login():
                        return await self._request(method, endpoint, json=json)
                    return None

                if 200 <= response.status < 300:
                    try:
                        resp = await response.json()
                        return resp
                    except aiohttp.ContentTypeError:
                        print(f"non-json response from {endpoint}")
                        return None

                print(f"{response.status} error: {endpoint}")
                return None

        except aiohttp.ClientError as e:
            print(f"network error: {e}")
            return None
    
    async def get_user_info(self) -> models.StudentProfile | None:
        data = await self._request("GET", "settings/user-info")
        return models.StudentProfile(**data) if data else None

    async def get_leaderboard(self, is_group: bool) -> models.StudentRatingList | None:
        endpoint = f"dashboard/progress/{'leader-group' if is_group else 'leader-stream'}"
        data = await self._request("GET", endpoint)
        if data:
            valid_items = [item for item in data if item.get("id") is not None]
            return models.StudentRatingList(root=valid_items)
        return None

    async def get_rewards(self) -> models.RewardsHistory | None:
        data = await self._request("GET", "dashboard/progress/activity")
        return models.RewardsHistory(root=data)

    async def get_activity(self) -> models.ActivityList | None:
        data = await self._request("GET", "progress/operations/student-visits")
        return models.ActivityList(root=data)

    async def get_homeworks(self, type: int, page: int, group_id: int = 8) -> models.HomeworkList | None:
        endpoint = f"homework/operations/list?page={page}&status={type}&type=0&group_id={group_id}"
        data = await self._request("GET", endpoint)
        return models.HomeworkList(root=data)

    async def get_homework_count(self, group_id: int = 8) -> models.HomeworkCounterList | None:
        endpoint = f"count/homework?type=0&group_id={group_id}"
        data = await self._request("GET", endpoint)
        return models.HomeworkCounterList(root=data)

    async def get_lesson_evaluations(self) -> models.EvalucationList | None:
        data = await self._request("GET", "feedback/students/evaluate-lesson-list")
        return models.EvalucationList(root=data)

    async def evaluate_lesson(self, data: models.EvalucateLessonData | dict) -> bool:
        if not isinstance(data, dict):
            data = data.model_dump()
        result = await self._request("POST", "feedback/students/evaluate-lesson", json=data)
        return result is not None