"""Tests for the cradle package version."""

import importlib.metadata

import cradle


def test_version_is_string():
    """Verify __version__ is a string."""
    assert isinstance(cradle.__version__, str)


def test_version_matches_metadata():
    """Verify __version__ matches the installed package metadata."""
    assert cradle.__version__ == importlib.metadata.version("rCradle")


def test_version_value():
    """Verify __version__ has the expected value from pyproject.toml."""
    assert cradle.__version__ == "0.1.0"
