"""
Gmail Agent CLI - Interactive Gmail CRM from your terminal

Usage:
    gmail chat           # Interactive chat with agent
    gmail inbox          # Show recent inbox emails
    gmail search "query" # Search emails
    gmail contacts       # Show contacts
    gmail init           # Initialize CRM database
    gmail sync           # Sync contacts
"""

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.columns import Columns
from typing import Optional
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from agent import agent, gmail

app = typer.Typer(
    name="gmail",
    help="Gmail CRM Agent - Read, search, and manage your Gmail from the terminal",
    invoke_without_command=True
)
console = Console()


@app.callback()
def main(ctx: typer.Context):
    """Gmail CRM Agent - Interactive Gmail management from your terminal."""
    # If no subcommand, launch interactive mode
    if ctx.invoked_subcommand is None:
        interactive()


COMMANDS = {
    '/inbox': 'Show recent emails',
    '/init': 'Initialize CRM database',
    '/identity': 'Show your email identity',
    '/search': 'Search emails',
    '/sync': 'Sync contacts from Gmail',
    '/contacts': 'Show cached contacts',
    '/unanswered': 'Find unanswered emails',
    '/help': 'Show all commands',
    '/quit': 'Exit',
}


class CommandCompleter(Completer):
    """Auto-complete that shows suggestions as you type."""
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith('/'):
            for cmd, desc in COMMANDS.items():
                if cmd.startswith(text):
                    yield Completion(cmd, start_position=-len(text), display_meta=desc)


def interactive():
    """Full interactive mode with command menu."""
    from pathlib import Path
    import os

    # Check if auth is set up (both LLM API key and Google tokens in .env)
    has_llm_key = any([
        os.getenv('OPENAI_API_KEY'),
        os.getenv('ANTHROPIC_API_KEY'),
        os.getenv('GEMINI_API_KEY'),
        os.getenv('OPENONION_API_KEY')
    ])
    has_google_token = os.getenv('GOOGLE_ACCESS_TOKEN')

    if not has_llm_key or not has_google_token:
        console.print(Panel(
            "[bold red]Google Auth Required[/bold red]\n\n"
            "You need to authenticate with Google first.\n"
            "This will open a browser to grant Gmail permissions.",
            title="[bold]Setup Required[/bold]",
            border_style="red",
            padding=(1, 2)
        ))

        from connectonion import pick, Shell, Agent

        choice = pick("Run authentication now?", [
            "Yes, run authentication",
            "No, I'll do it manually"
        ])

        if "Yes" in choice:
            console.print("\n[dim]Running authentication...[/dim]\n")
            shell = Shell()
            auth_agent = Agent("auth-helper", tools=[shell], log=False)
            auth_agent.input("Run these commands: co auth, then co auth google")
            console.print("\n[green]✓ Please restart the CLI.[/green]\n")
        else:
            console.print(Panel(
                "[bold yellow]Manual Setup Required[/bold yellow]\n\n"
                "[bold]Please run these commands:[/bold]\n\n"
                "1. [cyan]co auth[/cyan]          (authenticate LLM provider)\n"
                "2. [cyan]co auth google[/cyan]   (authenticate Google Gmail)\n\n"
                "Then restart this CLI.",
                border_style="yellow",
                padding=(1, 2)
            ))
        return

    # Check if CRM is initialized
    contacts_path = Path("data/contacts.csv")
    needs_init = not contacts_path.exists() or contacts_path.stat().st_size < 100

    if needs_init:
        console.print(Panel(
            "[bold yellow]CRM Not Initialized[/bold yellow]\n\n"
            "Initialize the CRM to:\n"
            "  • Extract contacts from emails\n"
            "  • Categorize people, services, notifications\n"
            "  • Set up your contact database\n\n"
            "[dim]Takes 2-3 minutes, only needs to run once.[/dim]",
            title="[bold]First Time Setup[/bold]",
            border_style="yellow",
            padding=(1, 2)
        ))

        from connectonion import pick
        choice = pick("Initialize CRM now?", [
            "Yes, initialize now",
            "Skip, I'll do it later with /init"
        ])

        if "Yes" in choice:
            console.print("\n[dim]Starting CRM initialization...[/dim]\n")
            from agent import init_crm_database
            with console.status("[bold blue]Processing...[/bold blue]"):
                result = init_crm_database()
            console.print(Panel(Markdown(result), title="[bold green]✓ Done[/bold green]", border_style="green"))

    # Session with auto-complete while typing and bottom toolbar
    style = Style.from_dict({
        'prompt': '#00d7ff bold',
        # Completion menu - dark bg, cyan commands, white descriptions
        'completion-menu': 'bg:#1e1e2e',
        'completion-menu.completion': 'bg:#1e1e2e #00d7ff',
        'completion-menu.completion.current': 'bg:#00d7ff #000000 bold',
        'completion-menu.meta': 'bg:#1e1e2e #cdd6f4',
        'completion-menu.meta.current': 'bg:#00d7ff #000000',
        # Bottom toolbar - subtle blue tint
        'bottom-toolbar': 'bg:#1e1e2e #89b4fa',
    })

    def bottom_toolbar():
        return HTML('<b>/</b> commands  <b>Tab</b> complete  <b>Enter</b> send  <b>Ctrl+C</b> exit')

    session = PromptSession(
        completer=CommandCompleter(),
        complete_while_typing=True,
        style=style,
        bottom_toolbar=bottom_toolbar
    )

    # Welcome with quick start guide
    console.print(Panel(
        "[bold cyan]Gmail CRM Agent[/bold cyan]\n\n"
        "[bold]Quick Start:[/bold]\n"
        "  [green]/inbox[/green]      Check your emails\n"
        "  [green]/contacts[/green]   View your contacts\n"
        "  [green]/help[/green]       See all commands\n\n"
        "[dim]Or just type naturally to chat with the AI agent![/dim]",
        title="[bold]Welcome[/bold]",
        border_style="cyan",
        padding=(1, 2)
    ))


    while True:
        try:
            user_input = session.prompt("\ngmail> ")

            if not user_input.strip():
                continue

            cmd = user_input.strip().lower()

            # Handle commands
            if cmd in ('/quit', '/exit', '/q', 'quit', 'exit'):
                console.print("[dim]Goodbye![/dim]")
                break

            elif cmd == '/help':
                # Grouped help menu
                essential = Panel(
                    "[green]/inbox[/green] [dim][n][/dim]\n"
                    "  Show recent emails\n\n"
                    "[green]/search[/green] [dim]query[/dim]\n"
                    "  Find specific emails\n\n"
                    "[green]/contacts[/green]\n"
                    "  View your contacts",
                    title="[bold green]Essential[/bold green]",
                    border_style="green"
                )
                manage = Panel(
                    "[yellow]/sync[/yellow]\n"
                    "  Update contacts\n\n"
                    "[yellow]/init[/yellow]\n"
                    "  Setup CRM database\n\n"
                    "[yellow]/unanswered[/yellow]\n"
                    "  Find pending replies",
                    title="[bold yellow]Manage[/bold yellow]",
                    border_style="yellow"
                )
                other = Panel(
                    "[dim]/identity[/dim]\n"
                    "  Your email config\n\n"
                    "[dim]/quit[/dim]\n"
                    "  Exit the app\n\n"
                    "[dim]/help[/dim]\n"
                    "  Show this menu",
                    title="[bold dim]Other[/bold dim]",
                    border_style="dim"
                )
                console.print(Columns([essential, manage, other], equal=True))
                console.print("\n[cyan]Tip:[/cyan] Just type naturally to chat with the AI agent!")

            elif cmd.startswith('/inbox'):
                parts = cmd.split()
                count = int(parts[1]) if len(parts) > 1 else 10
                with console.status("[bold blue]Fetching inbox...[/bold blue]"):
                    result = gmail.read_inbox(last=count)
                console.print(Panel(result, title="[bold]Inbox[/bold]", border_style="green"))

            elif cmd.startswith('/search'):
                query = user_input[7:].strip()
                if not query:
                    query = Prompt.ask("[dim]Search query[/dim]")
                with console.status(f"[bold blue]Searching...[/bold blue]"):
                    result = gmail.search_emails(query=query, max_results=10)
                console.print(Panel(result, title=f"[bold]Search: {query}[/bold]", border_style="yellow"))

            elif cmd == '/contacts':
                result = gmail.get_cached_contacts()
                console.print(Panel(result, title="[bold]Contacts[/bold]", border_style="cyan"))

            elif cmd == '/sync':
                with console.status("[bold blue]Syncing contacts...[/bold blue]"):
                    result = gmail.sync_contacts()
                console.print(Panel(result, title="[bold]Sync Complete[/bold]", border_style="green"))

            elif cmd == '/init':
                from agent import init_crm_database
                console.print("[dim]Initializing CRM (this may take a few minutes)...[/dim]")
                with console.status("[bold blue]Processing...[/bold blue]"):
                    result = init_crm_database()
                console.print(Panel(result, title="[bold green]CRM Initialized[/bold green]", border_style="green"))

            elif cmd == '/unanswered':
                with console.status("[bold blue]Finding unanswered emails...[/bold blue]"):
                    result = gmail.get_unanswered_emails()
                console.print(Panel(result, title="[bold]Unanswered[/bold]", border_style="red"))

            elif cmd == '/identity':
                with console.status("[bold blue]Getting identity...[/bold blue]"):
                    result = gmail.get_my_identity()
                console.print(Panel(result, title="[bold]Identity[/bold]", border_style="cyan"))

            elif cmd.startswith('/'):
                # Autocomplete: show matching commands
                base_cmd = cmd.split()[0]  # Get just the command part
                matches = [(c, desc) for c, desc in COMMANDS.items() if c.startswith(base_cmd)]
                if matches:
                    suggestions = '\n'.join(f"  [green]{c}[/green] - {desc}" for c, desc in matches)
                    console.print(Panel(suggestions, title=f"[bold]Commands matching '{base_cmd}'[/bold]", border_style="yellow"))
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]. Type /help for commands.")

            else:
                # Chat with agent
                console.print("[dim]Thinking...[/dim]")
                response = agent.input(user_input)
                console.print(Panel(
                    Markdown(response),
                    title="[bold blue]Agent[/bold blue]",
                    border_style="blue"
                ))

        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            continue  # Don't exit, just cancel current operation
        except EOFError:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            error_msg = str(e).lower()
            # Contextual error recovery
            if 'credential' in error_msg or 'auth' in error_msg or 'token' in error_msg:
                console.print(Panel(
                    f"[red]Authentication error[/red]\n\n"
                    f"[dim]{e}[/dim]\n\n"
                    "[bold]To fix:[/bold]\n"
                    "1. Run: [cyan]co auth google[/cyan]\n"
                    "2. Grant Gmail permissions\n"
                    "3. Try again",
                    title="[bold red]Auth Required[/bold red]",
                    border_style="red"
                ))
            elif 'network' in error_msg or 'connection' in error_msg or 'timeout' in error_msg:
                console.print(Panel(
                    f"[red]Network error[/red]\n\n"
                    f"[dim]{e}[/dim]\n\n"
                    "[bold]To fix:[/bold] Check your internet connection",
                    title="[bold red]Connection Failed[/bold red]",
                    border_style="red"
                ))
            else:
                console.print(Panel(
                    f"[red]{e}[/red]\n\n"
                    "[dim]Try /help to see available commands[/dim]",
                    title="[bold red]Error[/bold red]",
                    border_style="red"
                ))


@app.command()
def chat():
    """Interactive chat with Gmail agent."""

    console.print(Panel.fit(
        "[bold blue]Gmail Agent[/bold blue]\n"
        "Chat with your Gmail assistant. Type 'exit' or 'quit' to leave.",
        border_style="blue"
    ))

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")

            if user_input.lower() in ('exit', 'quit', 'q'):
                console.print("[dim]Goodbye![/dim]")
                break

            if not user_input.strip():
                continue

            with console.status("[bold blue]Thinking...[/bold blue]"):
                response = agent.input(user_input)

            console.print(Panel(
                Markdown(response),
                title="[bold blue]Agent[/bold blue]",
                border_style="blue"
            ))

        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/dim]")
            break


@app.command()
def inbox(
    count: int = typer.Option(10, "--count", "-n", help="Number of emails to show"),
    unread: bool = typer.Option(False, "--unread", "-u", help="Only show unread emails")
):
    """Show recent inbox emails."""

    with console.status("[bold blue]Fetching emails...[/bold blue]"):
        result = gmail.read_inbox(last=count, unread=unread)

    console.print(Panel(result, title="[bold]Inbox[/bold]", border_style="green"))


@app.command()
def search(
    query: str = typer.Argument(..., help="Gmail search query (e.g., 'from:alice@example.com')"),
    count: int = typer.Option(10, "--count", "-n", help="Number of results")
):
    """Search emails using Gmail query syntax."""

    with console.status(f"[bold blue]Searching for '{query}'...[/bold blue]"):
        result = gmail.search_emails(query=query, max_results=count)

    console.print(Panel(result, title=f"[bold]Search: {query}[/bold]", border_style="yellow"))


@app.command()
def contacts(
    count: int = typer.Option(20, "--count", "-n", help="Number of contacts to show")
):
    """Show contacts from cache (run 'sync' first)."""
    result = gmail.get_cached_contacts()

    console.print(Panel(result, title="[bold]Contacts[/bold]", border_style="cyan"))


@app.command()
def sync(
    max_emails: int = typer.Option(500, "--max", "-m", help="Max emails to scan"),
    exclude: str = typer.Option("openonion.ai,connectonion.com", "--exclude", "-e", help="Domains to exclude")
):
    """Sync contacts from Gmail (preserves CRM data)."""

    with console.status("[bold blue]Syncing contacts...[/bold blue]"):
        result = gmail.sync_contacts(max_emails=max_emails, exclude_domains=exclude)

    console.print(Panel(result, title="[bold]Sync Complete[/bold]", border_style="green"))


@app.command()
def init(
    max_emails: int = typer.Option(500, "--max", "-m", help="Max emails to scan"),
    top_n: int = typer.Option(10, "--top", "-t", help="Top contacts to analyze"),
    exclude: str = typer.Option("openonion.ai,connectonion.com", "--exclude", "-e", help="Domains to exclude")
):
    """Initialize CRM database (extracts and analyzes contacts)."""
    from agent import init_crm_database

    console.print(Panel(
        f"Initializing CRM from {max_emails} emails, analyzing top {top_n} contacts...\n"
        f"Excluding: {exclude}",
        title="[bold]CRM Init[/bold]",
        border_style="blue"
    ))

    with console.status("[bold blue]This may take a few minutes...[/bold blue]"):
        result = init_crm_database(max_emails=max_emails, top_n=top_n, exclude_domains=exclude)

    console.print(Panel(Markdown(result), title="[bold green]CRM Initialized[/bold green]", border_style="green"))


@app.command()
def read(
    email_id: str = typer.Argument(..., help="Gmail message ID")
):
    """Read full email body by ID."""

    with console.status("[bold blue]Fetching email...[/bold blue]"):
        result = gmail.get_email_body(email_id)

    console.print(Panel(result, title="[bold]Email[/bold]", border_style="blue"))


@app.command()
def unanswered(
    days: int = typer.Option(120, "--days", "-d", help="Look back N days (default: 120)"),
    count: int = typer.Option(20, "--count", "-n", help="Max results")
):
    """Find emails you haven't replied to."""

    with console.status("[bold blue]Finding unanswered emails...[/bold blue]"):
        result = gmail.get_unanswered_emails(within_days=days, max_results=count)

    console.print(Panel(result, title="[bold]Unanswered Emails[/bold]", border_style="red"))


@app.command()
def identity(
    detect: bool = typer.Option(False, "--detect", "-d", help="Detect Cloudflare/forwarded addresses from received emails")
):
    """Show your email addresses and organization domains."""

    with console.status("[bold blue]Getting identity...[/bold blue]"):
        if detect:
            result = gmail.detect_all_my_emails(max_emails=100)
        else:
            result = gmail.get_my_identity()

    console.print(Panel(result, title="[bold]Your Identity[/bold]", border_style="cyan"))


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask the agent")
):
    """Ask a single question to the Gmail agent."""

    with console.status("[bold blue]Thinking...[/bold blue]"):
        response = agent.input(question)

    console.print(Panel(Markdown(response), title="[bold blue]Agent[/bold blue]", border_style="blue"))


if __name__ == "__main__":
    app()