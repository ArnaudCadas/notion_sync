from __future__ import annotations
import json
from aiohttp.client import ClientSession
from typing import List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from github.issue import Issue


class GitHubManager:

    def __init__(self,
                 session: ClientSession,
                 repo: str,
                 owner: str,
                 token: str) -> None:
        self.session = session
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/"
        self.headers = {
            "Authorization": token,
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }

    async def get_issue(self, number: int) -> Dict:
        url = self.base_url + f"issues/{number}"
        async with self.session.get(url, headers=self.headers) as response:
            return await response.json()

    async def get_all_issues(self) -> List[Dict]:
        url = self.base_url + "issues"
        async with self.session.get(url, headers=self.headers) as response:
            return await response.json()

    async def post_issue(self, issue: Issue) -> None:
        url = self.base_url + "issues"
        data = json.dumps({
            "title": issue.title,
            "body": issue.body
        })
        async with self.session.post(url, headers=self.headers, data=data) as response:
            response.raise_for_status()

    async def update_issue(self, issue: Issue) -> None:
        url = self.base_url + f"issues/{issue.number}"
        data = json.dumps({
            "body": issue.body
        })
        async with self.session.patch(url, headers=self.headers, data=data) as response:
            response.raise_for_status()

    async def get_reviews(self, number: int) -> Dict:
        url = self.base_url + f"pulls/{number}/reviews"
        async with self.session.get(url, headers=self.headers) as response:
            return await response.json()
