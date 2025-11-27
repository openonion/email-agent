"""Test the Email Agent functionality."""

import os
import shutil
import pytest
from connectonion import Memory
from agent import agent


def test_agent_creation():
    """Test that agent is created with correct configuration."""
    assert agent.name == "email-agent"
    assert agent.max_iterations == 15


def test_agent_has_email_tools():
    """Test that agent has access to email tools."""
    tool_names = [tool.name for tool in agent.tools]

    assert "read_inbox" in tool_names
    assert "search_emails" in tool_names
    assert "send" in tool_names
    assert "mark_read" in tool_names


def test_agent_has_memory_tools():
    """Test that agent has access to memory tools."""
    tool_names = [tool.name for tool in agent.tools]

    assert "write_memory" in tool_names
    assert "read_memory" in tool_names
    assert "list_memories" in tool_names
    assert "search_memory" in tool_names


def test_memory_class_integration():
    """Test that Memory class can be used as tool source."""
    memory = Memory(memory_dir="test_mem")

    assert hasattr(memory, "write_memory")
    assert hasattr(memory, "read_memory")
    assert hasattr(memory, "list_memories")
    assert hasattr(memory, "search_memory")

    if os.path.exists("test_mem"):
        shutil.rmtree("test_mem")


@pytest.mark.real_api
def test_agent_basic_query():
    """Test agent can process a basic query (requires API key).

    Run with: pytest tests/ -m real_api
    """
    result = agent.input("List my memories")
    assert result is not None
    assert isinstance(result, str)
