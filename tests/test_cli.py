"""Tests for Gmail Agent CLI."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


class TestDoToday:
    """Tests for do_today function."""

    def test_date_query_format(self):
        """Verify date query format is correct."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
        query = f"after:{yesterday}"

        assert query.startswith("after:")
        date_part = query.split(':', 1)[1]
        assert len(date_part.split('/')) == 3  # YYYY/MM/DD

    @patch('cli.core.gmail')
    @patch('cli.core.agent')
    @patch('cli.core.SlashCommand')
    def test_calls_search_with_correct_query(self, mock_cmd_class, mock_agent, mock_gmail):
        """Verify do_today calls search_emails with yesterday's date."""
        mock_cmd = Mock()
        mock_cmd.prompt = "Analyze: {emails}"
        mock_cmd_class.load.return_value = mock_cmd
        mock_gmail.search_emails.return_value = "email results"
        mock_agent.input.return_value = "briefing"

        from cli.core import do_today
        result = do_today()

        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
        mock_gmail.search_emails.assert_called_once_with(
            query=f"after:{yesterday}",
            max_results=50
        )

    @patch('cli.core.gmail')
    @patch('cli.core.agent')
    @patch('cli.core.SlashCommand')
    def test_replaces_emails_placeholder(self, mock_cmd_class, mock_agent, mock_gmail):
        """Verify {emails} placeholder is replaced in prompt."""
        mock_cmd = Mock()
        mock_cmd.prompt = "Analyze these: {emails}"
        mock_cmd_class.load.return_value = mock_cmd
        mock_gmail.search_emails.return_value = "test email data"
        mock_agent.input.return_value = "result"

        from cli.core import do_today
        do_today()

        mock_agent.input.assert_called_once_with("Analyze these: test email data")

    @patch('cli.core.SlashCommand')
    def test_returns_error_when_command_not_found(self, mock_cmd_class):
        """Verify error message when today command not found."""
        mock_cmd_class.load.return_value = None

        from cli.core import do_today
        result = do_today()

        assert "not found" in result


class TestDoInbox:
    """Tests for do_inbox function."""

    @patch('cli.core.gmail')
    def test_calls_read_inbox_with_defaults(self, mock_gmail):
        """Verify do_inbox calls read_inbox with default parameters."""
        mock_gmail.read_inbox.return_value = "inbox emails"

        from cli.core import do_inbox
        result = do_inbox()

        mock_gmail.read_inbox.assert_called_once_with(last=10, unread=False)
        assert result == "inbox emails"

    @patch('cli.core.gmail')
    def test_passes_custom_count(self, mock_gmail):
        """Verify custom count is passed to read_inbox."""
        mock_gmail.read_inbox.return_value = "emails"

        from cli.core import do_inbox
        do_inbox(count=25)

        mock_gmail.read_inbox.assert_called_once_with(last=25, unread=False)

    @patch('cli.core.gmail')
    def test_passes_unread_filter(self, mock_gmail):
        """Verify unread filter is passed to read_inbox."""
        mock_gmail.read_inbox.return_value = "unread emails"

        from cli.core import do_inbox
        do_inbox(unread=True)

        mock_gmail.read_inbox.assert_called_once_with(last=10, unread=True)


class TestDoSearch:
    """Tests for do_search function."""

    @patch('cli.core.gmail')
    def test_calls_search_emails(self, mock_gmail):
        """Verify do_search calls search_emails correctly."""
        mock_gmail.search_emails.return_value = "search results"

        from cli.core import do_search
        result = do_search(query="from:test@example.com")

        mock_gmail.search_emails.assert_called_once_with(
            query="from:test@example.com",
            max_results=10
        )
        assert result == "search results"

    @patch('cli.core.gmail')
    def test_passes_custom_count(self, mock_gmail):
        """Verify custom count is passed to search_emails."""
        mock_gmail.search_emails.return_value = "results"

        from cli.core import do_search
        do_search(query="subject:test", count=50)

        mock_gmail.search_emails.assert_called_once_with(
            query="subject:test",
            max_results=50
        )


class TestDoAsk:
    """Tests for do_ask function."""

    @patch('cli.core.agent')
    def test_passes_question_to_agent(self, mock_agent):
        """Verify do_ask passes question to agent.input."""
        mock_agent.input.return_value = "agent response"

        from cli.core import do_ask
        result = do_ask("What emails need my attention?")

        mock_agent.input.assert_called_once_with("What emails need my attention?")
        assert result == "agent response"


class TestDoIdentity:
    """Tests for do_identity function."""

    @patch('cli.core.gmail')
    def test_returns_identity_without_detect(self, mock_gmail):
        """Verify do_identity calls get_my_identity by default."""
        mock_gmail.get_my_identity.return_value = "user@example.com"

        from cli.core import do_identity
        result = do_identity()

        mock_gmail.get_my_identity.assert_called_once()
        assert result == "user@example.com"

    @patch('cli.core.gmail')
    def test_detects_all_emails_when_flag_set(self, mock_gmail):
        """Verify do_identity calls detect_all_my_emails when detect=True."""
        mock_gmail.detect_all_my_emails.return_value = "all emails"

        from cli.core import do_identity
        result = do_identity(detect=True)

        mock_gmail.detect_all_my_emails.assert_called_once_with(max_emails=100)
        assert result == "all emails"


class TestDoUnanswered:
    """Tests for do_unanswered function."""

    @patch('cli.core.gmail')
    def test_calls_with_defaults(self, mock_gmail):
        """Verify do_unanswered calls with default parameters."""
        mock_gmail.get_unanswered_emails.return_value = "unanswered"

        from cli.core import do_unanswered
        result = do_unanswered()

        mock_gmail.get_unanswered_emails.assert_called_once_with(
            older_than_days=120,
            max_results=20
        )

    @patch('cli.core.gmail')
    def test_passes_custom_parameters(self, mock_gmail):
        """Verify custom parameters are passed correctly."""
        mock_gmail.get_unanswered_emails.return_value = "emails"

        from cli.core import do_unanswered
        do_unanswered(days=30, count=50)

        mock_gmail.get_unanswered_emails.assert_called_once_with(
            older_than_days=30,
            max_results=50
        )


@pytest.mark.real_api
class TestIntegration:
    """Integration tests requiring real API access.

    Run with: pytest tests/ -m real_api
    """

    def test_today_command_returns_result(self):
        """Verify /today returns a non-empty result."""
        from cli.core import do_today
        result = do_today()

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    def test_inbox_returns_emails(self):
        """Verify inbox returns email data."""
        from cli.core import do_inbox
        result = do_inbox(count=5)

        assert result is not None
        assert isinstance(result, str)