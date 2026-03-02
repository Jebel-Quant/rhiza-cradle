import importlib.metadata

import cradle


def test_version_is_string():
    assert isinstance(cradle.__version__, str)


def test_version_matches_metadata():
    assert cradle.__version__ == importlib.metadata.version("rCradle")


def test_version_value():
    assert cradle.__version__ == "0.1.0"
