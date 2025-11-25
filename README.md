# Gmail Agent

**Your Gmail inbox, powered by AI.** Read, search, analyze, and manage your emails using natural language commands in an interactive terminal interface.

Built with [ConnectOnion](https://github.com/openonion/connectonion) - the Python framework for AI agents.

## Features

- **Interactive CLI** - Beautiful terminal interface with numbered menus and real-time email browsing
- **Natural Language Search** - Ask questions about your emails in plain English
- **Smart Authentication** - Automatic setup flow guides you through Google OAuth
- **Email Management** - Read, search, send, and reply to emails
- **Memory System** - Remembers context across conversations
- **Gmail Query Support** - Full Gmail search syntax (from:, to:, subject:, date filters)

## Quick Start

### Installation

```bash
pip install connectonion
git clone https://github.com/openonion/gmail-agent.git
cd gmail-agent
pip install -r requirements.txt
```

### Run the CLI

```bash
python cli.py
```

The first time you run it, the agent will guide you through:
1. Authenticating with OpenOnion (for LLM access)
2. Connecting your Google account (for Gmail access)

After authentication, you'll see an interactive menu:

```
┌─────────────────────────────────────┐
│ Gmail Agent                         │
│                                     │
│ What would you like to do?          │
│                                     │
│  ❯ 1  Interactive chat              │
│    2  Read inbox                    │
│    3  Read sent emails              │
│    4  Search emails                 │
│    5  Exit                          │
└─────────────────────────────────────┘
```

### Example Queries

Once in interactive mode, ask anything about your emails:

```
You: Show me unread emails from the last week
You: Find all emails with attachments from alice@example.com
You: Who should I reply to today?
You: What did I send yesterday?
You: Search for emails about "project alpha"
```

## Authentication

The agent requires two authentications:

### 1. OpenOnion (LLM Provider)

```bash
co auth
```

Provides access to managed LLM APIs (GPT, Claude, Gemini) with free credits.

### 2. Google OAuth (Gmail Access)

```bash
co auth google
```

Grants permissions for:
- Gmail read (`gmail.readonly`)
- Gmail send (`gmail.send`)
- Gmail modify (`gmail.modify`)
- Calendar read (`calendar.readonly`)

All credentials are stored securely in `.env` file.

## CLI Commands

### Interactive Mode

```bash
python cli.py
# Select "1. Interactive chat"
```

Natural language conversation with the agent. Ask questions, search emails, get summaries.

### Direct Commands

```python
from agent import agent

# Read recent inbox
agent.input("Show me my last 10 emails")

# Search specific sender
agent.input("Find emails from bob@company.com this month")

# Complex queries
agent.input("Show unread emails with attachments from last week")

# Send email
agent.input("""
Send email to alice@example.com
Subject: Follow-up
Body: Hi Alice, following up on our conversation...
""")
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
gmail-agent/
├── cli.py              # Interactive terminal interface
├── agent.py            # Main agent configuration
├── prompts/            # System prompts for different modes
│   └── main.txt        # Default agent instructions
├── data/               # Local data storage
├── tests/              # Test suite
└── .env                # Credentials (auto-generated)
```

## How It Works

### Architecture

```python
from connectonion import Agent, Gmail

# Gmail tool provides 9 operations
gmail = Gmail()

# Agent combines LLM + Gmail tools
agent = Agent(
    name="gmail-agent",
    tools=[gmail],
    model="co/gemini-2.5-pro",  # Using managed API
    system_prompt=prompt
)

# Natural language → Tool calls → Results
agent.input("Show me unread emails")
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
GOOGLE_SCOPES=gmail.send,gmail.readonly,gmail.modify,calendar.readonly
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

## Use Cases

### Personal Email Management

```
"Show me emails I haven't replied to this week"
"Find all receipts with attachments"
"Who are my most frequent contacts?"
```

### Professional Communication

```
"Draft a follow-up email to bob@company.com about the Q4 proposal"
"Show me all meeting invites for next week"
"Find emails from my manager about the project"
```

### Email Triage

```
"Which emails need urgent replies?"
"Show me unread emails from VIP contacts"
"Find threads I participated in this month"
```

## Philosophy

**"Gmail is your database"** - No manual data entry. No separate CRM. Just direct Gmail access with AI understanding.

**"Tools first, features later"** - Start with solid low-level primitives (read, search, send), then build higher-level analysis.

**"Keep simple things simple"** - 2-minute setup, natural language commands, automatic authentication.

## Resources

- **ConnectOnion Docs**: https://docs.connectonion.com
- **Discord Community**: https://discord.gg/4xfD9k8AUF
- **Gmail API Reference**: https://developers.google.com/gmail/api
- **OpenOnion Platform**: https://openonion.ai

## Contributing

Contributions welcome! Please read the contributing guidelines and submit PRs.

## License

MIT License - See LICENSE file for details

## Built With

- [ConnectOnion](https://github.com/openonion/connectonion) - AI agent framework
- [Gmail API](https://developers.google.com/gmail/api) - Email access
- [Rich](https://github.com/Textualize/rich) - Terminal UI
- [Google Auth](https://google-auth.oauthlib.readthedocs.io/) - OAuth authentication

---

**Made by the OpenOnion team** - Building the future of AI agents
