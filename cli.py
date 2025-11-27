"""
Gmail Agent CLI - Interactive Gmail CRM from your terminal

Usage:
    gmail              # Interactive mode (default)
    gmail inbox        # Show recent emails
    gmail today        # Daily briefing
    gmail ask "query"  # One-shot question
    gmail init         # Initialize CRM database
"""

from cli import app

if __name__ == "__main__":
    app()
