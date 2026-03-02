# rhiza-cradle

**rhiza-cradle** is a command-line tool for scaffolding new repositories from
[Copier](https://copier.readthedocs.io) templates. It keeps a registry of named
templates in a local config file and wraps the full `copier run-copy` + GitHub
bootstrap workflow into a single command.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- [GitHub CLI](https://cli.github.com/) (`gh`) — only required for the final
  `gh repo create` step shown in the post-create instructions

## Installation

```bash
# run without installing (recommended)
uvx rhiza-cradle --help

# or install into the active environment
uv add rhiza-cradle
```

## Usage

### List available templates

```bash
rhiza-cradle list
```

Prints a table of all templates registered in `~/.cradle/config.yaml`.

### Create a project

```bash
rhiza-cradle create <template> --name <project-name> --username <github-username>
```

| Flag | Short | Default | Description |
|---|---|---|---|
| `--name` | `-n` | _(required)_ | Name of the new project directory |
| `--username` | `-u` | _(required)_ | GitHub username / org that will own the repo |
| `--description` | `-d` | `"A project created with Cradle CLI"` | Short project description |
| `--visibility` | `-v` | `private` | GitHub visibility: `private`, `public`, or `internal` |

**Example**

```bash
rhiza-cradle create package \
  --name my-library \
  --username acme-org \
  --description "Acme's core Python library" \
  --visibility public
```

After the template is copied, the tool prints the exact `gh`/`git` commands
needed to push the new repo to GitHub.

## Configuration

Templates are defined in `~/.cradle/config.yaml`. The file is created
automatically on first run with the following built-in templates:

```yaml
templates:
  experiments:
    url: https://github.com/tschm/experiments
    description: Template for experimental projects with Marimo notebooks
  package:
    url: https://github.com/tschm/package
    description: Template for Python packages with PyPI publishing support
  paper:
    url: https://github.com/tschm/paper
    description: Template for academic papers with LaTeX support
```

Add your own entries using the same structure:

```yaml
templates:
  my-template:
    url: https://github.com/your-org/your-template
    description: My custom template
```

## Development

```bash
# install dependencies
make install

# run tests
make test

# lint & format
make fmt
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for commit conventions, branching
strategy, and pull-request guidelines.

## License

[MIT](LICENSE) — Jebel Quant Research
