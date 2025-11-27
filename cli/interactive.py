"""
Interactive mode for Email Agent CLI.

Full-featured REPL with slash commands and autocomplete.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.columns import Columns
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML

from agent import agent
from .core import (
    do_inbox, do_search, do_contacts, do_sync,
    do_init, do_unanswered, do_identity, do_today, do_ask
)

console = Console()

COMMANDS = {
    '/today': 'Daily email briefing',
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
    # Session with auto-complete while typing and bottom toolbar
    style = Style.from_dict({
        'prompt': '#00d7ff bold',
        'completion-menu': 'bg:#1e1e2e',
        'completion-menu.completion': 'bg:#1e1e2e #00d7ff',
        'completion-menu.completion.current': 'bg:#00d7ff #000000 bold',
        'completion-menu.meta': 'bg:#1e1e2e #cdd6f4',
        'completion-menu.meta.current': 'bg:#00d7ff #000000',
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
            user_input = session.prompt("\ngmail> ")

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

            elif cmd.startswith('/'):
                # Autocomplete: show matching commands
                base_cmd = cmd.split()[0]
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
