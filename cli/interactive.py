"""
Interactive mode for Email Agent CLI.

Full-featured REPL with slash commands and autocomplete using ConnectOnion TUI.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.columns import Columns

from connectonion.tui import Input, StaticProvider, StatusBar

from agent import agent
from .core import (
    do_inbox, do_search, do_contacts, do_sync,
    do_init, do_unanswered, do_identity, do_today, do_ask
)
from .contacts_provider import ContactProvider

console = Console()


def _set_env_flag(key: str, value: str):
    """Set a flag in .env file."""
    from pathlib import Path
    env_path = Path('.env')

    # Read existing content
    lines = []
    if env_path.exists():
        lines = env_path.read_text().splitlines()

    # Update or add the key
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f'{key}='):
            lines[i] = f'{key}={value}'
            found = True
            break

    if not found:
        lines.append(f'{key}={value}')

    # Write back
    env_path.write_text('\n'.join(lines) + '\n')

# Commands with descriptions and icons for StaticProvider
COMMANDS = [
    ("/today", "/today", "Daily email briefing", "📅"),
    ("/inbox", "/inbox", "Show recent emails", "📥"),
    ("/search", "/search", "Search emails", "🔍"),
    ("/contacts", "/contacts", "View your contacts", "👥"),
    ("/sync", "/sync", "Sync contacts from Gmail", "🔄"),
    ("/init", "/init", "Initialize CRM database", "🗄️"),
    ("/unanswered", "/unanswered", "Find unanswered emails", "⏳"),
    ("/identity", "/identity", "Show your email identity", "🆔"),
    ("/link-gmail", "/link-gmail", "Connect Gmail account", "🔗"),
    ("/link-outlook", "/link-outlook", "Connect Outlook account", "🔗"),
    ("/help", "/help", "Show all commands", "❓"),
    ("/quit", "/quit", "Exit", "👋"),
]


def interactive():
    """Full interactive mode with command menu."""
    # Providers for autocomplete
    command_provider = StaticProvider(COMMANDS)
    contact_provider = ContactProvider()

    # Hints (always visible) and rotating tips
    hints = ["/ commands", "@ contacts", "Enter submit", "Ctrl+D quit"]
    tips = [
        "Try /today for your daily email briefing",
        "Use @ to mention contacts in your messages",
        "Type naturally to chat with the AI agent",
    ]

    # Welcome with quick start guide
    console.print(Panel(
        "[bold cyan]Email Agent[/bold cyan]\n\n"
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
            # Status bar at top
            status = StatusBar([
                ("📧", "Email Agent", "cyan"),
                ("🤖", f"co/{agent.llm.model}", "magenta"),
            ])
            console.print()
            console.print(status.render())

            # Input with hints and rotating tips
            user_input = Input(
                triggers={
                    "/": command_provider,
                    "@": contact_provider,
                },
                hints=hints,
                tips=tips,
                divider=True,
            ).run()

            if not user_input.strip():
                continue

            cmd = user_input.strip().lower()

            # Handle commands
            if cmd in ('/quit', '/exit', '/q', 'quit', 'exit'):
                console.print("[dim]Goodbye![/dim]")
                break

            elif cmd == '/help':
                essential = Panel(
                    "[green]/today[/green]\n"
                    "  Daily email briefing\n\n"
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

            elif cmd == '/today':
                console.print("[dim]Analyzing today's emails...[/dim]")
                with console.status("[bold blue]Fetching and analyzing...[/bold blue]"):
                    result = do_today()
                console.print(Panel(Markdown(result), title="[bold blue]Today's Briefing[/bold blue]", border_style="blue"))

            elif cmd.startswith('/inbox'):
                parts = cmd.split()
                count = int(parts[1]) if len(parts) > 1 else 10
                with console.status("[bold blue]Fetching inbox...[/bold blue]"):
                    result = do_inbox(count=count)
                console.print(Panel(result, title="[bold]Inbox[/bold]", border_style="green"))

            elif cmd.startswith('/search'):
                query = user_input[7:].strip()
                if not query:
                    query = Prompt.ask("[dim]Search query[/dim]")
                with console.status(f"[bold blue]Searching...[/bold blue]"):
                    result = do_search(query=query)
                console.print(Panel(result, title=f"[bold]Search: {query}[/bold]", border_style="yellow"))

            elif cmd == '/contacts':
                result = do_contacts()
                console.print(Panel(result, title="[bold]Contacts[/bold]", border_style="cyan"))

            elif cmd == '/sync':
                with console.status("[bold blue]Syncing contacts...[/bold blue]"):
                    result = do_sync()
                console.print(Panel(result, title="[bold]Sync Complete[/bold]", border_style="green"))

            elif cmd == '/init':
                console.print("[dim]Initializing CRM (this may take a few minutes)...[/dim]")
                with console.status("[bold blue]Processing...[/bold blue]"):
                    result = do_init()
                console.print(Panel(result, title="[bold green]CRM Initialized[/bold green]", border_style="green"))

            elif cmd == '/unanswered':
                with console.status("[bold blue]Finding unanswered emails...[/bold blue]"):
                    result = do_unanswered()
                console.print(Panel(result, title="[bold]Unanswered[/bold]", border_style="red"))

            elif cmd == '/identity':
                with console.status("[bold blue]Getting identity...[/bold blue]"):
                    result = do_identity()
                console.print(Panel(result, title="[bold]Identity[/bold]", border_style="cyan"))

            elif cmd == '/link-gmail':
                import subprocess
                subprocess.run(['co', 'auth', 'google'])
                _set_env_flag('LINKED_GMAIL', 'true')
                console.print("\n[green]✓ Gmail connected. Restart the CLI to use it.[/green]")

            elif cmd == '/link-outlook':
                import subprocess
                subprocess.run(['co', 'auth', 'microsoft'])
                _set_env_flag('LINKED_OUTLOOK', 'true')
                console.print("\n[green]✓ Outlook connected. Restart the CLI to use it.[/green]")

            elif cmd.startswith('/'):
                # Unknown command - suggest using /help
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
            continue
        except EOFError:
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception as e:
            error_msg = str(e).lower()
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
