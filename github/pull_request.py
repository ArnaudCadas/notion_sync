from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


from github.review import Review, ReviewState, create_review_state
from github.manager import GitHubManager


class PullRequestStatus(Enum):
    OPENED = "open"
    CLOSED = "closed"
    MERGED = "merged"


@dataclass
class PullRequest:
    number: int
    link: str
    body: str
    status: PullRequestStatus
    reviews: List[Review]

    @classmethod
    async def from_event(cls, event: Dict, manager: GitHubManager) -> PullRequest:
        action = event["action"]
        pull_request_payload = event["pull_request"]

        number = pull_request_payload["number"]
        link = pull_request_payload["html_url"]
        body = pull_request_payload.get("body", "")
        if action == "closed":
            if pull_request_payload["merged"]:
                status = PullRequestStatus.MERGED
            else:
                status = PullRequestStatus.CLOSED
        else:
            status = PullRequestStatus.OPENED

        reviews_params = {}
        # We create an initial dictionaries of the latest review for each author.
        reviews_payloads = await manager.get_reviews(number=number)
        for review_payload in reviews_payloads:
            author = review_payload["user"]["login"]
            state = create_review_state(state=review_payload["state"])
            current_state = reviews_params.get(author, ReviewState.REQUESTED)
            # Approved and changes requested reviews have the highest priority.
            # Commented reviews have a higher priority than requested reviews.
            replace_state_condition = (
                ((state == ReviewState.COMMENTED)
                 & (current_state == ReviewState.REQUESTED))
                | (state == ReviewState.APPROVED)
                | (state == ReviewState.CHANGES_REQUESTED)
            )
            if replace_state_condition:
                reviews_params[author] = state
        # We force the review state to requested for all requested reviewers.
        for requested_reviewer in pull_request_payload["requested_reviewers"]:
            author = requested_reviewer["login"]
            reviews_params[author] = ReviewState.REQUESTED
        reviews = [Review(author=author, state=state)
                   for author, state in reviews_params.items()]
        pull_request = cls(
            number=number, link=link, body=body, status=status, reviews=reviews)
        return pull_request
