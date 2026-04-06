import httpx
from typing import Optional, List, Dict, Any
from cli.config import get_token

BASE_URL = "http://localhost:8000"


class DevSwingsClient:
    def __init__(self):
        self.base_url = BASE_URL

    def _get_headers(self):
        token = get_token()
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    async def login(self, email: str, password: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
            )
            if response.status_code == 200:
                return response.json()["access_token"]
            return None

    async def register(self, email: str, password: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "password": password},
            )
            return response.status_code == 200

    async def get_my_stats(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            params = {}
            if project_id:
                params["project_id"] = project_id
            response = await client.get(
                f"{self.base_url}/insights/me",
                params=params,
                headers=self._get_headers(),
            )
            if response.status_code == 200:
                return response.json()
            return {}

    async def get_projects(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects", headers=self._get_headers()
            )
            if response.status_code == 200:
                return response.json()
            return []

    async def create_project(self, name: str, goal: int) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/projects",
                json={"name": name, "weekly_goal_hours": goal},
                headers=self._get_headers(),
            )
            return response.status_code == 200

    async def get_streak(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/streaks/me", headers=self._get_headers()
            )
            if response.status_code == 200:
                return response.json()
            return {"current_streak": 0}

    async def create_session(
        self, project_id: Optional[str], energy_start: int, mood: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            payload = {"energy_start": energy_start}
            if project_id:
                payload["project_id"] = project_id
            if mood:
                payload["mood"] = mood

            response = await client.post(
                f"{self.base_url}/sessions", json=payload, headers=self._get_headers()
            )
            if response.status_code == 200:
                return response.json()
            return None

    async def end_session(
        self,
        session_id: str,
        energy_end: int,
        flow_achieved: bool,
        notes: Optional[str] = None,
        blockers: Optional[str] = None,
    ) -> bool:
        async with httpx.AsyncClient() as client:
            payload = {"energy_end": energy_end, "flow_achieved": flow_achieved}
            if notes:
                payload["notes"] = notes
            if blockers:
                payload["blockers"] = blockers

            response = await client.post(
                f"{self.base_url}/sessions/{session_id}/end",
                json=payload,
                headers=self._get_headers(),
            )
            return response.status_code == 200

    async def create_commit(self, sha: str, message: str, project_id: Optional[str] = None) -> bool:
        async with httpx.AsyncClient() as client:
            payload = {"sha": sha, "message": message}
            if project_id:
                payload["project_id"] = project_id
            
            response = await client.post(
                f"{self.base_url}/commits",
                json=payload,
                headers=self._get_headers(),
            )
            return response.status_code == 200

    async def batch_create_commits(self, commits: List[Dict[str, Any]]) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/commits/batch",
                json=commits,
                headers=self._get_headers(),
            )
            return response.status_code == 200
