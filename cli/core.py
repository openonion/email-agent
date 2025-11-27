"""
Core logic functions for Gmail Agent CLI.

These functions are shared by CLI commands and interactive slash commands.
"""

from connectonion import SlashCommand
from agent import agent, gmail


def do_inbox(count: int = 10, unread: bool = False) -> str:
    return gmail.read_inbox(last=count, unread=unread)


def do_search(query: str, count: int = 10) -> str:
    return gmail.search_emails(query=query, max_results=count)


def do_contacts() -> str:
    return gmail.get_cached_contacts()


def do_sync(max_emails: int = 500, exclude: str = "openonion.ai,connectonion.com") -> str:
    return gmail.sync_contacts(max_emails=max_emails, exclude_domains=exclude)


def do_init(max_emails: int = 500, top_n: int = 10, exclude: str = "openonion.ai,connectonion.com") -> str:
    from agent import init_crm_database
    return init_crm_database(max_emails=max_emails, top_n=top_n, exclude_domains=exclude)


def do_unanswered(days: int = 120, count: int = 20) -> str:
    return gmail.get_unanswered_emails(older_than_days=days, max_results=count)


def do_identity(detect: bool = False) -> str:
    if detect:
        return gmail.detect_all_my_emails(max_emails=100)
    return gmail.get_my_identity()


def do_today() -> str:
    """Run /today command using SlashCommand."""
    from datetime import datetime, timedelta
    cmd = SlashCommand.load("today")
    if not cmd:
        return "Command 'today' not found in commands/"

    # Get today's emails
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
    emails = gmail.search_emails(query=f"after:{yesterday}", max_results=50)

    # Replace {emails} placeholder in prompt
    prompt = cmd.prompt.replace("{emails}", emails)
    return agent.input(prompt)


def do_ask(question: str) -> str:
    return agent.input(question)
