# Contributing To `rich-argparse`
For clear bug-fixes just submit a PR. For new features or if there is any doubt in how to fix a bug you may want to open an issue to discuss the feature prior to starting work.

## Environment Setup
You can use `tox` ([documentation](https://tox.wiki/en/latest/index.html)) to setup a virtual environment for `rich_argparse` and install dependencies.

```sh
cd /path/to/rich_argparse
tox --devenv venv
```

## Development
There's a few possible ways to experiment with changes to `rich-argparse`. The simplest is to create a dummy python file in the same folder as the repo containing an `argparse` setup and running it as you make the changes.

Another possibility is to tell your package manager to use your local copy of `rich_argparse` as the `argparse` formatter in your own project and then running that project's executable with `--help` as you make changes. With the caveat that you should understand that this approach will make changes to your project's virtual environment (and `.lock` files, if they exist) and thus you should know what you are doing, to install the local copy of `rich_argparse` as a package in another project called `my_project`:

#### If `my_project` Uses Poetry
You can add this line to the `tool.poetry.dependencies` section of `my_project/pyproject.toml`:

```toml
[tool.poetry.dependencies]
rich_argparse = {path = "/path/to/rich-argparse", develop = true}
```

### Code Style
For those using VS Code there's [preconfigured settings](.vscode/) in the repo that will ensure that your contributions are styled correctly.
