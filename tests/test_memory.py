"""Test the Memory system functionality."""

import os
import shutil
import pytest
from connectonion import Memory


@pytest.fixture
def test_memory():
    """Create a Memory instance with a test directory."""
    test_dir = "test_memories_temp"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    memory = Memory(memory_dir=test_dir)
    yield memory

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_write_memory(test_memory):
    """Test writing a memory."""
    result = test_memory.write_memory("test-note", "This is a test note")
    assert "saved" in result.lower()
    assert "test-note" in result


def test_read_memory(test_memory):
    """Test reading a memory."""
    test_memory.write_memory("test-note", "This is a test note")
    result = test_memory.read_memory("test-note")
    assert "This is a test note" in result
    assert "test-note" in result


def test_read_nonexistent_memory(test_memory):
    """Test reading a memory that doesn't exist."""
    result = test_memory.read_memory("does-not-exist")
    assert "not found" in result.lower()


def test_list_memories_empty(test_memory):
    """Test listing memories when none exist."""
    result = test_memory.list_memories()
    assert "no memories" in result.lower() or "0" in result


def test_list_memories_with_content(test_memory):
    """Test listing memories with content."""
    test_memory.write_memory("note-1", "First note")
    test_memory.write_memory("note-2", "Second note")

    result = test_memory.list_memories()
    assert "note-1" in result
    assert "note-2" in result


def test_memory_persistence(test_memory):
    """Test that memories persist across instances."""
    test_memory.write_memory("persistent", "This should persist")

    new_memory = Memory(memory_dir=test_memory.memory_dir)
    result = new_memory.read_memory("persistent")
    assert "This should persist" in result


def test_invalid_key_sanitization(test_memory):
    """Test that invalid characters in keys are sanitized."""
    result = test_memory.write_memory("test@#$%note", "Content")
    assert "saved" in result.lower() or "invalid" in result.lower()

    # If saved (after sanitization)
    if "saved" in result.lower():
        result = test_memory.read_memory("testnote")
        assert "Content" in result


def test_markdown_content(test_memory):
    """Test that markdown content is preserved."""
    markdown = "# Header\n\n- Item 1\n- Item 2\n\n**Bold text**"
    test_memory.write_memory("markdown-test", markdown)

    result = test_memory.read_memory("markdown-test")
    assert "# Header" in result
    assert "**Bold text**" in result
