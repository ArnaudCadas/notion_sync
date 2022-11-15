from __future__ import annotations
import re
from typing import List, Dict
from dataclasses import dataclass

from github.pull_request import PullRequest
from github.manager import GitHubManager


@dataclass
class Issue:
    number: int
    title: str
    body: str = ""
    linked_pull_request: PullRequest = None

    @classmethod
    def from_dict(cls, payload: Dict) -> Issue:
        issue_number = payload["number"]
        issue_title = payload["title"]
        issue_body = payload["body"]
        return cls(number=issue_number, title=issue_title, body=issue_body)

    def link_pull_request(self, pull_request: PullRequest) -> None:
        self.linked_pull_request = pull_request

    def update_body(self, body: str) -> bool:
        if body != self.body:
            self.body = body
            return True
        else:
            return False


def create_unique_issues_from_payloads(
        issues_payloads: List[Dict]) -> Dict[str, Issue]:
    unique_issues = {}
    for issue_payload in issues_payloads:
        issue = Issue.from_dict(payload=issue_payload)
        duplicated_issue = unique_issues.get(issue.title, False)
        if duplicated_issue:
            if issue.number > duplicated_issue.number:
                unique_issues[issue.title] = issue
        else:
            unique_issues[issue.title] = issue
    return unique_issues


async def parse_issues(
        pull_request: PullRequest,
        github_manager: GitHubManager) -> List[Issue]:
    issues = []
    issue_pattern = r'(?:close(?:\b|s|d)|fix(?:\b|es|ed)|resolve(?:\b|s|d)) #[0-9]+'
    matches = re.findall(issue_pattern, pull_request.body)
    for match in matches:
        issue_number = match.split("#")[1]
        issue_payload = await github_manager.get_issue(number=issue_number)
        issue = Issue.from_dict(payload=issue_payload)
        issue.link_pull_request(pull_request=pull_request)
        issues.append(issue)
    return issues
