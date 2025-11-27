"""
Gmail Agent - Gmail reading and management with memory

Purpose: Read, search, and manage your actual Gmail inbox
Pattern: Use ConnectOnion Gmail class + Memory system + GoogleCalendar + Shell + Plugins
"""

from connectonion import Agent, Memory, Gmail, GoogleCalendar, WebFetch, Shell, TodoList
from connectonion.useful_plugins import react


# Create shared tool instances (Gmail defaults to data/emails.csv and data/contacts.csv)
memory = Memory(memory_file="data/memory.md")
gmail = Gmail()  # Uses default paths: data/emails.csv, data/contacts.csv
calendar = GoogleCalendar()  # For calendar events and meeting invites
web = WebFetch()  # For analyzing contact domains
shell = Shell()  # For running shell commands (e.g., get current date)
todo = TodoList()  # For tracking multi-step tasks

# Create init sub-agent for CRM database setup
init_crm = Agent(
    name="crm-init",
    system_prompt="prompts/crm_init.md",
    tools=[gmail, memory, calendar, web],  # Gmail + Memory + Calendar + WebFetch
    max_iterations=30,
    model="co/gemini-2.5-pro",
    log=False  # Don't create separate log file
)


def init_crm_database(max_emails: int = 500, top_n: int = 10, exclude_domains: str = "openonion.ai,connectonion.com") -> str:
    """Initialize CRM database by extracting and analyzing top contacts.

    Args:
        max_emails: Number of emails to scan for contacts (default: 500)
        top_n: Number of top contacts to analyze and save (default: 10)
        exclude_domains: Comma-separated domains to exclude (your org domains)

    Returns:
        Summary of initialization process including number of contacts analyzed
    """
    result = init_crm.input(
        f"Initialize CRM: Extract top {top_n} contacts from {max_emails} emails.\n"
        f"IMPORTANT: Use get_all_contacts(max_emails={max_emails}, exclude_domains=\"{exclude_domains}\")\n"
        f"Then use AI judgment to categorize and analyze the most important contacts."
    )
    # Return clear completion message so main agent knows not to call again
    return f"CRM INITIALIZATION COMPLETE. Data saved to memory. Use read_memory() to access:\n- crm:all_contacts\n- crm:needs_reply\n- crm:init_report\n- contact:email@example.com\n\nDetails: {result}"


# Create main agent with Gmail, Memory, Calendar, Shell, Todo, AND init wrapper function
agent = Agent(
    name="gmail-agent",
    system_prompt="prompts/gmail_agent.md",
    tools=[gmail, memory, calendar, shell, todo, init_crm_database],
    plugins=[react],  # ReAct pattern for better reasoning
    max_iterations=15,
    model="co/gemini-2.5-pro",
)

# Example usage
if __name__ == "__main__":
    print("=== Gmail CRM Agent ===\n")

    # Example 1: Initialize CRM database using wrapper function
    print("1. Initialize CRM database...")
    result = agent.input(
        "Initialize the CRM database with top 5 contacts from recent 500 emails"
    )
    print(result)

    print("\n" + "="*50 + "\n")

    # Example 2: Query from MEMORY (should NOT re-fetch from API)
    print("2. Query from memory (should be fast)...")
    result = agent.input("Who do I email the most? Check memory first.")
    print(result)
