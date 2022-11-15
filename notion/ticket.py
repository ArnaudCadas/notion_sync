from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, TYPE_CHECKING
from enum import Enum

from notion.property import Property, PROPERTY_TYPE_TO_SUBCLASS
from notion.block import Block, ParagraphBlock
from notion.objects import RichText, Text
from notion.manager import NotionManager
from github.pull_request import PullRequestStatus
if TYPE_CHECKING:
    from github.issue import Issue


class TicketStatus(Enum):
    BACKLOG = "Backlog"
    BACKLOG_PRIO = "Backlog - prio"
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    PREPROD = "Preprod/QA"
    COMPLETED = "Completed"


PULL_REQUEST_STATUS_TO_TICKET_STATUS = {
    PullRequestStatus.OPENED: TicketStatus.REVIEW,
    PullRequestStatus.MERGED: TicketStatus.PREPROD,
    PullRequestStatus.CLOSED: TicketStatus.COMPLETED
}


@dataclass
class Ticket:
    id: str
    properties: List[Property] = field(default_factory=list)
    body: List[Block] = field(default_factory=list)

    @property
    def title(self) -> str:
        name_property = self.get_property(name="Name")
        return name_property.value

    @classmethod
    def from_page(cls, page: Dict, body: List[Dict] = None) -> Ticket:
        ticket_id = page["id"]
        properties = []
        for property_name, property_value in page["properties"].items():
            property_subclass: Property = PROPERTY_TYPE_TO_SUBCLASS.get(
                property_value["type"], None)
            if property_subclass is None:
                raise NotImplementedError(
                    f"The {property_value['type']} property is not implemented.")
            properties.append(
                property_subclass.from_dict(
                    property_dict={property_name: property_value})
            )
        ticket_body = []
        if body is not None:
            for block in body:
                if block["type"] == "paragraph":
                    ticket_body.append(
                        ParagraphBlock.from_dict(block_dict=block))
        ticket = cls(id=ticket_id, properties=properties, body=ticket_body)
        return ticket

    def get_property(self, name: str) -> Property:
        for ticket_property in self.properties:
            if ticket_property.name == name:
                return ticket_property
        raise ValueError(f"The ticket does not have the {name} property.")

    def update_property(self, name: str, value: Any) -> None:
        ticket_property = self.get_property(name=name)
        ticket_property.update(value=value)

    def update(self, issue: Issue) -> None:
        if issue.title != self.title:
            raise ValueError(
                "The issue title is not the same as the ticket title.")

        pull_request = issue.linked_pull_request
        pull_request_status = pull_request.status
        self.update_property(
            name="PR", value=pull_request_status.value)
        self.update_property(
            name="Status",
            value=PULL_REQUEST_STATUS_TO_TICKET_STATUS[pull_request_status].value)
        pull_request_number_text = [
            RichText(
                object=Text(
                    content=f"#{pull_request.number}", link=pull_request.link),
                plain_text=f"#{pull_request.number}",
                href=pull_request.link)]
        self.update_property(name="PR number", value=pull_request_number_text)
        reviewers = ", ".join(
            [f"{review}" for review in issue.linked_pull_request.reviews])
        if reviewers:
            reviewers_text = [
                RichText(object=Text(content=reviewers), plain_text=reviewers)]
        else:
            reviewers_text = []
        self.update_property(name="Reviewers", value=reviewers_text)

    def create_issue_body(self) -> str:
        tags = self.get_property(name="Task")
        issue_body = ["".join(f"[{tag}]" for tag in tags.value)]
        complexity = self.get_property(name="Points")
        if complexity.value is not None:
            issue_body.append(f"[{complexity.value} points]")
        for block in self.body:
            if isinstance(block, ParagraphBlock):
                issue_body.append("".join(f"{rich_text}"
                                          for rich_text in block.text))
        return "\n".join(issue_body)


async def update_ticket_from_issue(
        issue: Issue, notion_manager: NotionManager) -> None:
    pages = await notion_manager.get_pages(titles=[issue.title])
    page = pages[0]
    ticket = Ticket.from_page(page=page)
    ticket.update(issue=issue)
    await notion_manager.post_ticket(ticket=ticket)
