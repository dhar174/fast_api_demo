"""Fixtures for the existing live-server chat scripts when run under pytest."""

from collections.abc import Iterator

import pytest
import requests


@pytest.fixture
def session_id() -> Iterator[str]:
    """Create a real chat session for tests that require an existing session."""
    base_url = "http://localhost:8002"
    response = requests.post(
        f"{base_url}/chat", data={"message": "Hello!"}, timeout=120
    )
    response.raise_for_status()
    created_session_id = response.json()["session_id"]
    try:
        yield created_session_id
    finally:
        response = requests.delete(
            f"{base_url}/chat/history/{created_session_id}", timeout=30
        )
        response.raise_for_status()
