from __future__ import annotations
import json
from aiohttp.client import ClientSession
from typing import List, Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from notion.ticket import Ticket


class NotionManager:
    def __init__(self,
                 session: ClientSession,
                 database_id: str,
                 token: str) -> None:
        self.session = session
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1/"
        self.headers = {
            "Authorization": token,
            "Notion-Version": "2021-08-16",
            "Content-Type": "application/json"
        }

    async def post_ticket(self, ticket: Ticket) -> None:
        url = self.base_url + f"pages/{ticket.id}"
        data = json.dumps({
            "properties": {
                ticket_property.name: ticket_property.to_dict()
                for ticket_property in ticket.properties
            }
        })
        async with self.session.patch(url, headers=self.headers, data=data) as response:
            response.raise_for_status()

    async def get_pages(self, titles: List[str] = None) -> List[Dict]:
        url = self.base_url + f"databases/{self.database_id}/query"
        if titles:
            data = json.dumps({
                "filter": {
                    "or": [
                        {
                            "property": "Name",
                            "title": {"equals": title}
                        } for title in titles
                    ]
                }
            })
        else:
            data = json.dumps({
                "filter":
                    {
                        "property": "Status",
                        "select": {"does_not_equal": "Completed"}
                    }
            })
        async with self.session.post(url, headers=self.headers, data=data) as response:
            json_response = await response.json()
            return json_response["results"]

    async def get_page_content(self, page_id: str) -> List[Dict]:
        url = self.base_url + f"blocks/{page_id}/children"
        async with self.session.get(url, headers=self.headers) as response:
            json_response = await response.json()
            return json_response["results"]
