"""Tests for cradle.config module."""

from pathlib import Path

import pytest
import yaml

from cradle.config import DEFAULT_CONFIG, _ensure_config_file, _read_config, get_all_templates


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    """Write a minimal config file to a temp directory and return its path."""
    cfg = tmp_path / "config.yaml"
    yaml.dump(DEFAULT_CONFIG, cfg.open("w"))
    return cfg


class TestEnsureConfigFile:
    """Tests for _ensure_config_file."""

    def test_creates_dir_and_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Creates the config directory and file when neither exists."""
        config_dir = tmp_path / ".cradle"
        config_file = config_dir / "config.yaml"

        monkeypatch.setattr("cradle.config.CONFIG_DIR", config_dir)
        monkeypatch.setattr("cradle.config.CONFIG_FILE", config_file)

        _ensure_config_file()

        assert config_dir.exists()
        assert config_file.exists()

    def test_written_content_is_default_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """File written by _ensure_config_file contains DEFAULT_CONFIG."""
        config_dir = tmp_path / ".cradle"
        config_file = config_dir / "config.yaml"

        monkeypatch.setattr("cradle.config.CONFIG_DIR", config_dir)
        monkeypatch.setattr("cradle.config.CONFIG_FILE", config_file)

        _ensure_config_file()

        with config_file.open() as f:
            content = yaml.safe_load(f)

        assert content == DEFAULT_CONFIG

    def test_does_not_overwrite_existing_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Does not overwrite the config file when it already exists."""
        config_dir = tmp_path / ".cradle"
        config_dir.mkdir()
        config_file = config_dir / "config.yaml"
        custom = {"templates": {"custom": {"url": "https://example.com", "description": "custom"}}}
        yaml.dump(custom, config_file.open("w"))

        monkeypatch.setattr("cradle.config.CONFIG_DIR", config_dir)
        monkeypatch.setattr("cradle.config.CONFIG_FILE", config_file)

        _ensure_config_file()

        with config_file.open() as f:
            content = yaml.safe_load(f)

        assert content == custom


class TestReadConfig:
    """Tests for _read_config."""

    def test_reads_provided_config_file(self, config_file: Path) -> None:
        """Returns the parsed YAML from the given path."""
        result = _read_config(config_file)
        assert result == DEFAULT_CONFIG

    def test_returns_dict(self, config_file: Path) -> None:
        """Return type is a dict."""
        result = _read_config(config_file)
        assert isinstance(result, dict)

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        """Raises an error when the given path does not exist."""
        with pytest.raises(FileNotFoundError):
            _read_config(tmp_path / "nonexistent.yaml")


class TestGetAllTemplates:
    """Tests for get_all_templates."""

    def test_returns_all_default_templates(self, config_file: Path) -> None:
        """Returns all three default templates."""
        templates = get_all_templates(config_file)
        assert set(templates.keys()) == {"experiments", "package", "paper"}

    def test_each_template_has_url_and_description(self, config_file: Path) -> None:
        """Every template entry contains 'url' and 'description' keys."""
        templates = get_all_templates(config_file)
        for name, info in templates.items():
            assert "url" in info, f"Template '{name}' missing 'url'"
            assert "description" in info, f"Template '{name}' missing 'description'"

    def test_returns_empty_dict_when_no_templates_key(self, tmp_path: Path) -> None:
        """Returns an empty dict when the config has no 'templates' section."""
        cfg = tmp_path / "config.yaml"
        yaml.dump({}, cfg.open("w"))
        assert get_all_templates(cfg) == {}

    def test_custom_template_is_returned(self, tmp_path: Path) -> None:
        """Returns a custom template written to the config file."""
        custom = {"templates": {"my-tpl": {"url": "https://example.com", "description": "custom"}}}
        cfg = tmp_path / "config.yaml"
        yaml.dump(custom, cfg.open("w"))

        templates = get_all_templates(cfg)
        assert "my-tpl" in templates
        assert templates["my-tpl"]["url"] == "https://example.com"
