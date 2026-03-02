"""Tests for cradle.cli module."""

import copier
import pytest
from typer.testing import CliRunner

from cradle.cli import app

runner = CliRunner()


class TestListTemplates:
    """Tests for the list command."""

    def test_no_templates_shows_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Prints an error message when no templates are available."""
        monkeypatch.setattr("cradle.cli.get_all_templates", lambda: {})
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No templates found" in result.output

    def test_templates_shown_in_output(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Renders template name, description, and URL."""
        templates = {
            "my-tpl": {"description": "My template", "url": "https://example.com/tpl"},
        }
        monkeypatch.setattr("cradle.cli.get_all_templates", lambda: templates)
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "my-tpl" in result.output
        assert "My template" in result.output
        assert "https://example.com/tpl" in result.output

    def test_templates_sorted_alphabetically(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Templates are displayed in sorted order."""
        templates = {
            "z-tpl": {"description": "Z", "url": "https://z.example.com"},
            "a-tpl": {"description": "A", "url": "https://a.example.com"},
        }
        monkeypatch.setattr("cradle.cli.get_all_templates", lambda: templates)
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert result.output.index("a-tpl") < result.output.index("z-tpl")

    def test_template_without_description_shows_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Shows 'No description available' when template has no description key."""
        monkeypatch.setattr("cradle.cli.get_all_templates", lambda: {"bare": {"url": "https://example.com"}})
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No description available" in result.output


class TestCreateProject:
    """Tests for the create command."""

    def test_unknown_template_exits_with_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Exits with code 1 and prints an error when the template is not found."""
        monkeypatch.setattr("cradle.cli.get_all_templates", lambda: {"existing": {"url": "https://x.com"}})
        result = runner.invoke(app, ["create", "unknown", "--name", "proj", "--username", "user"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_unknown_template_lists_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Lists available templates when the requested template is missing."""
        monkeypatch.setattr("cradle.cli.get_all_templates", lambda: {"existing": {"url": "https://x.com"}})
        result = runner.invoke(app, ["create", "unknown", "--name", "proj", "--username", "user"])
        assert "existing" in result.output

    def test_template_without_url_exits_with_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Exits with code 1 when the template has no URL defined."""
        monkeypatch.setattr("cradle.cli.get_all_templates", lambda: {"my-tpl": {"description": "no url here"}})
        result = runner.invoke(app, ["create", "my-tpl", "--name", "proj", "--username", "user"])
        assert result.exit_code == 1
        assert "no URL" in result.output

    def test_successful_creation_exits_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Exits with code 0 and prints success on a valid template."""
        monkeypatch.setattr(
            "cradle.cli.get_all_templates",
            lambda: {"my-tpl": {"url": "https://example.com/tpl", "description": "desc"}},
        )
        monkeypatch.setattr(copier, "run_copy", lambda **kwargs: None)
        result = runner.invoke(app, ["create", "my-tpl", "--name", "myproject", "--username", "alice"])
        assert result.exit_code == 0
        assert "successfully" in result.output

    def test_copier_exception_exits_with_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Exits with code 1 and prints the error message when copier raises."""
        monkeypatch.setattr(
            "cradle.cli.get_all_templates",
            lambda: {"my-tpl": {"url": "https://example.com/tpl"}},
        )

        def fail(**kwargs):
            raise RuntimeError("copy failed")  # noqa: TRY003

        monkeypatch.setattr(copier, "run_copy", fail)
        result = runner.invoke(app, ["create", "my-tpl", "--name", "myproject", "--username", "alice"])
        assert result.exit_code == 1
        assert "copy failed" in result.output

    def test_default_description_passed_to_copier(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Passes the default description to copier when none is provided."""
        monkeypatch.setattr(
            "cradle.cli.get_all_templates",
            lambda: {"my-tpl": {"url": "https://example.com/tpl"}},
        )
        captured: dict = {}

        def capture(**kwargs):
            captured.update(kwargs)

        monkeypatch.setattr(copier, "run_copy", capture)
        runner.invoke(app, ["create", "my-tpl", "--name", "myproject", "--username", "alice"])
        assert captured["data"]["description"] == "A project created with Cradle CLI"

    def test_copier_receives_correct_arguments(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Passes the correct src_path, dst_path, and data dict to copier."""
        monkeypatch.setattr(
            "cradle.cli.get_all_templates",
            lambda: {"my-tpl": {"url": "https://example.com/tpl"}},
        )
        captured: dict = {}

        def capture(**kwargs):
            captured.update(kwargs)

        monkeypatch.setattr(copier, "run_copy", capture)
        runner.invoke(
            app,
            ["create", "my-tpl", "--name", "myproject", "--username", "alice", "--description", "custom desc"],
        )
        assert captured["src_path"] == "https://example.com/tpl"
        assert captured["dst_path"] == "myproject"
        assert captured["data"]["project_name"] == "myproject"
        assert captured["data"]["username"] == "alice"
        assert captured["data"]["description"] == "custom desc"
        assert captured["data"]["repository"] == "https://github.com/alice/myproject"
