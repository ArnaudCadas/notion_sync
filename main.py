import json
import argparse
import asyncio
import aiohttp
from typing import Dict

from github.pull_request import PullRequest
from github.issue import Issue, parse_issues, create_unique_issues_from_payloads
from github.manager import GitHubManager
from notion.ticket import Ticket, update_ticket_from_issue
from notion.manager import NotionManager


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--event")
    args = parser.parse_args()

    event_payload = json.loads(args.event)
    print(json.dumps(event_payload, indent=4))

    async with aiohttp.ClientSession() as session:
        github_manager = GitHubManager(
            session=session,
            owner=...,
            repo=...,
            token=...)
        notion_manager = NotionManager(
            session=session,
            database_id=...,
            token=...)

        await notion_to_github_sync(
            notion_manager=notion_manager, github_manager=github_manager)
        await github_to_notion_sync(
            event_payload=event_payload, github_manager=github_manager,
            notion_manager=notion_manager)


async def sync_page(page: Dict,
                    unique_issues: Dict[str, Issue],
                    notion_manager: NotionManager,
                    github_manager: GitHubManager) -> None:
    page_id = page["id"]
    page_content = await notion_manager.get_page_content(page_id=page_id)
    ticket = Ticket.from_page(page=page, body=page_content)
    title = ticket.title
    body = ticket.create_issue_body()
    if title in unique_issues:
        issue = unique_issues[title]
        updated = issue.update_body(body=body)
        if updated:
            await github_manager.update_issue(issue=issue)
    else:
        issue = Issue(number=0, title=title, body=body)
        await github_manager.post_issue(issue=issue)


async def notion_to_github_sync(
        notion_manager: NotionManager, github_manager: GitHubManager):
    pages = await notion_manager.get_pages()
    issues_payloads = await github_manager.get_all_issues()
    unique_issues = create_unique_issues_from_payloads(issues_payloads)
    await asyncio.gather(*[
        sync_page(
            page=page, unique_issues=unique_issues,
            notion_manager=notion_manager, github_manager=github_manager)
        for page in pages])


async def github_to_notion_sync(
        event_payload: Dict, github_manager: GitHubManager,
        notion_manager: NotionManager):
    pull_request = await PullRequest.from_event(
        event=event_payload, manager=github_manager)
    issues = await parse_issues(
        pull_request=pull_request, github_manager=github_manager)
    # Notion fetch tickets and update them.
    await asyncio.gather(*[
        update_ticket_from_issue(issue=issue, notion_manager=notion_manager)
        for issue in issues])


if __name__ == "__main__":
    asyncio.run(main())
