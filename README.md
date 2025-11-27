<p align="center">
  <img src="https://connectonion.com/logo.png" alt="Email Agent" width="120">
</p>

<h1 align="center">Email Agent</h1>

<p align="center">
  <strong>Your Gmail inbox, powered by AI.</strong><br>
  Read, search, analyze, and manage your emails using natural language.
</p>

<p align="center">
  <a href="https://github.com/openonion/email-agent/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="License"></a>
  <a href="https://discord.gg/4xfD9k8AUF"><img src="https://img.shields.io/discord/1234567890?color=7289da&label=discord" alt="Discord"></a>
  <a href="https://docs.connectonion.com"><img src="https://img.shields.io/badge/docs-connectonion.com-green" alt="Docs"></a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#usage">Usage</a> •
  <a href="#documentation">Docs</a> •
  <a href="#community">Community</a>
</p>

---

Built with [ConnectOnion](https://connectonion.com) - the Python framework for AI agents.

## Features

- **Interactive CLI** - Beautiful terminal interface with slash commands and autocomplete
- **Natural Language Search** - Ask questions about your emails in plain English
- **Smart Authentication** - Automatic setup flow guides you through Google OAuth
- **Email Management** - Read, search, send, and reply to emails
- **Calendar Integration** - Schedule meetings and Google Meet calls
- **CRM Database** - Build and manage a contact database from your emails
- **Memory System** - Remembers context across conversations
- **Gmail Query Support** - Full Gmail search syntax (from:, to:, subject:, date filters)

## Quick Start

### Installation

```bash
pip install connectonion
git clone https://github.com/openonion/email-agent.git
cd email-agent
pip install -r requirements.txt
```

### Run the CLI

```bash
python cli.py
```

The first time you run it, the agent will guide you through:
1. Authenticating with OpenOnion (for LLM access)
2. Connecting your Google account (for Gmail and Calendar access)

After authentication, you'll see an interactive prompt with autocomplete:

```
┌────────────────────────────────────────────────┐
│ Email Agent                                    │
│                                                │
│ Quick Start:                                   │
│   /inbox      Check your emails                │
│   /contacts   View your contacts               │
│   /help       See all commands                 │
│                                                │
│ Or just type naturally to chat with the AI!   │
└────────────────────────────────────────────────┘

gmail>
```

### Example Usage

**Slash Commands:**
```
/today          Daily email briefing with priorities
/inbox          Show recent emails
/search query   Search your emails
/contacts       View your contact database
/unanswered     Find emails you haven't replied to
/init           Initialize CRM database (first time)
/help           See all commands
```

**Natural Language - The agent is proactive:**

```
gmail> Schedule a meeting with sarah@acme.com

🔍 Checking your calendar... You're free tomorrow 2-4pm.
📧 Found recent emails about "API integration timeline".

I suggest:
  'Acme Integration Sync' - Tomorrow 2:00pm, 30 min

Book it? (yes/no)
```

```
gmail> What emails need my attention?

Found 3 emails waiting for your reply:

1. David (investor) - 5 days waiting
   Asked for Q3 revenue and team size.

   Draft reply:
   > Hey David, Q3: $XXk revenue, 12 person team.
   > Happy to chat more if helpful. Best

2. Lisa (client) - 2 days waiting
   Asked about enterprise pricing.

   Draft reply:
   > Hi Lisa, Enterprise is $15/user/month, 50 seat min.
   > Want me to send a formal quote? Cheers

3. Tom (applicant) - 7 days waiting
   Following up on application.

   Draft reply:
   > Hi Tom, Still reviewing, will update by Friday. Thanks!

Send all three? Or edit any?
```

```
gmail> Catch me up on the Notion deal

📊 Notion Deal Status:

Contact: Lisa (lisa@notion.so) - Enterprise Sales
Timeline:
  - Nov 18: You asked about pricing tiers
  - Nov 20: Lisa sent contract ($15/user, 50 seats min)
  - ⚠️ No response yet - 7 days waiting

Here's a reply:

> Hi Lisa,
> Thanks for the contract. Reviewed and ready to move forward.
> What are the next steps?
> Best

Send it?
```

## Authentication

The agent requires two authentications:

### 1. OpenOnion (LLM Provider)

```bash
co auth
```

Provides access to managed LLM APIs (GPT, Claude, Gemini) with free credits.

### 2. Google OAuth (Gmail + Calendar Access)

```bash
co auth google
```

Grants permissions for:
- Gmail read (`gmail.readonly`)
- Gmail send (`gmail.send`)
- Gmail modify (`gmail.modify`)
- Calendar full access (`calendar`) - for scheduling meetings and creating Google Meet links

All credentials are stored securely in `.env` file.

## CLI Commands

### Interactive Mode (Default)

```bash
python cli.py
```

Interactive REPL with slash commands and autocomplete. Just type `/` to see available commands.

### Direct CLI Commands

```bash
python cli.py inbox              # Show recent emails
python cli.py inbox -n 20        # Show 20 emails
python cli.py inbox --unread     # Only unread emails
python cli.py search "from:bob"  # Search emails
python cli.py today              # Daily briefing
python cli.py contacts           # Show cached contacts
python cli.py sync               # Sync contacts from Gmail
python cli.py init               # Initialize CRM database
python cli.py unanswered         # Find unanswered emails
python cli.py ask "question"     # One-shot question
```

### Python API

```python
from agent import agent

# Read recent inbox
agent.input("Show me my last 10 emails")

# Search specific sender
agent.input("Find emails from bob@company.com this month")

# Schedule meetings (proactive - agent finds free slots)
agent.input("Schedule a meeting with alice@example.com")

# Send email (agent drafts based on context)
agent.input("Send a follow-up email to bob@example.com")
```

## Gmail Search Syntax

The agent supports full Gmail query syntax:

**Filter by sender/recipient:**
```
from:alice@example.com
to:bob@example.com
```

**Filter by content:**
```
subject:invoice
meeting
```

**Filter by status:**
```
is:unread
is:important
is:starred
```

**Filter by attachments:**
```
has:attachment
filename:pdf
```

**Filter by date:**
```
after:2025/11/01
before:2025/12/01
newer_than:7d
older_than:1m
```

**Combine filters:**
```
from:alice is:unread subject:project
from:bob has:attachment after:2025/11/01
```

## Project Structure

```
email-agent/
├── cli.py              # Entry point
├── cli/                # CLI package
│   ├── __init__.py     # Exports app
│   ├── core.py         # Core logic (do_inbox, do_search, etc.)
│   ├── setup.py        # Auth and CRM setup checks
│   ├── interactive.py  # Interactive REPL with autocomplete
│   └── commands.py     # Typer CLI commands
├── agent.py            # Main agent + CRM init sub-agent
├── prompts/            # System prompts
│   ├── gmail_agent.md  # Main agent instructions
│   └── crm_init.md     # CRM initialization agent
├── commands/           # Slash command definitions
│   ├── today.md        # /today command
│   ├── inbox.md        # /inbox command
│   └── search.md       # /search command
├── data/               # Local data storage
│   ├── contacts.csv    # Contact database
│   ├── emails.csv      # Email cache
│   └── memory.md       # Agent memory
├── tests/              # Test suite
└── .env                # Credentials (auto-generated)
```

## How It Works

### Architecture

```python
from connectonion import Agent, Gmail, GoogleCalendar, Memory, Shell, TodoList
from connectonion.useful_plugins import react

# Tools
gmail = Gmail()           # 17 email operations
calendar = GoogleCalendar()  # 9 calendar operations
memory = Memory()         # Persistent memory
shell = Shell()           # Shell commands (date, etc.)
todo = TodoList()         # Task tracking

# Agent combines LLM + tools + plugins
agent = Agent(
    name="email-agent",
    tools=[gmail, calendar, memory, shell, todo],
    plugins=[react],      # ReAct reasoning pattern
    model="co/gemini-2.5-pro",
    system_prompt="prompts/gmail_agent.md"
)

# Natural language → Tool calls → Results
agent.input("Schedule a meeting with alice@example.com")
```

### Authentication Flow

1. **First run**: Agent detects missing credentials
2. **Prompts user**: "Run authentication now?" with numbered options
3. **Option 1 - Automatic**: Agent runs `co auth` and `co auth google` for you
4. **Option 2 - Manual**: Shows clear instructions with commands to run
5. **Stores tokens**: Saves to `.env` for future sessions

### Memory System

The agent maintains conversation context:

```python
# First query
agent.input("Show me emails from Alice")
# → Searches and shows results

# Follow-up (remembers context)
agent.input("Get the full text of the second one")
# → Knows which email you mean
```

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Using Tox

```bash
tox                    # Run all tests
tox -e coverage        # With coverage report
tox -e lint            # Code quality checks
```

### Test Organization

```
tests/
├── test_memory.py     # Memory system tests
└── test_agent.py      # Agent functionality
```

See [TESTING.md](TESTING.md) for detailed testing guide.

## Configuration

### Environment Variables

All stored in `.env` (auto-generated during setup):

```bash
# LLM Provider (OpenOnion)
OPENONION_API_KEY=...
AGENT_ADDRESS=0x...

# Google OAuth
GOOGLE_ACCESS_TOKEN=...
GOOGLE_REFRESH_TOKEN=...
GOOGLE_TOKEN_EXPIRES_AT=...
GOOGLE_SCOPES=gmail.send,gmail.readonly,gmail.modify,calendar
GOOGLE_EMAIL=your.email@gmail.com
```

### Security

- ✅ All data stays in your Gmail
- ✅ No external database
- ✅ OAuth tokens encrypted and locally stored
- ✅ Read-only by default (send requires explicit command)

**Never commit `.env` to git** - it's already in `.gitignore`

## Troubleshooting

### "Not authenticated" Error

Run authentication:
```bash
co auth
co auth google
```

### "Insufficient credits" Error

Your OpenOnion account needs credits. Contact support or add credits via the dashboard.

### "Permission denied" on Gmail

Re-authenticate with Google:
```bash
co auth google
# Make sure to grant all requested permissions
```

### Token Expired

Tokens auto-refresh, but if you see errors:
```bash
rm .env
python cli.py  # Will prompt for fresh authentication
```

## What Can You Do?

### Daily Workflow
```
gmail> /today
```
Get a prioritized briefing: urgent emails, today's meetings, follow-ups needed.

### Email Triage
```
gmail> Help me clean up my inbox
```
Agent categorizes emails, drafts replies for important ones, suggests what to archive.

### Meeting Scheduling
```
gmail> Set up a call with Mike next week
```
Agent finds free slots, checks your recent conversation with Mike, proposes meeting with smart title.

### Contact Research
```
gmail> Who is john@company.com?
```
Agent searches all emails, analyzes relationship history, summarizes key interactions.

### Batch Replies
```
gmail> Reply to all unanswered emails
```
Agent finds gaps, drafts replies matching your style, sends with one confirmation.

### Deal Tracking
```
gmail> What's happening with the Acme deal?
```
Agent traces full email history, shows timeline, identifies pending actions.

## Philosophy

**"Gmail is your database"** - No manual data entry. No separate CRM. Just direct Gmail access with AI understanding.

**"Tools first, features later"** - Start with solid low-level primitives (read, search, send), then build higher-level analysis.

**"Keep simple things simple"** - 2-minute setup, natural language commands, automatic authentication.

## Documentation

- **[ConnectOnion Docs](https://docs.connectonion.com)** - Full framework documentation
- **[Getting Started](https://docs.connectonion.com/getting-started)** - Step-by-step tutorial
- **[Tools Reference](https://docs.connectonion.com/tools)** - Gmail, Calendar, Memory tools
- **[Gmail API Reference](https://developers.google.com/gmail/api)** - Google's official docs

## Community

Join our community to get help, share projects, and chat with the team:

- **[Discord](https://discord.gg/4xfD9k8AUF)** - Chat and support
- **[GitHub Issues](https://github.com/openonion/email-agent/issues)** - Bug reports and feature requests
- **[ConnectOnion Website](https://connectonion.com)** - Framework homepage

## Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest tests/ -v`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Security

Found a security issue? Please report it privately via Discord or GitHub.

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

## Built With

- [ConnectOnion](https://connectonion.com) - AI agent framework
- [Gmail API](https://developers.google.com/gmail/api) - Email access
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [Typer](https://typer.tiangolo.com/) - CLI framework

---

<p align="center">
  <a href="https://connectonion.com">connectonion.com</a> •
  <a href="https://docs.connectonion.com">docs</a> •
  <a href="https://discord.gg/4xfD9k8AUF">discord</a>
</p>

<p align="center">
  <sub>Built with by the <a href="https://openonion.ai">OpenOnion</a> team</sub>
</p>
