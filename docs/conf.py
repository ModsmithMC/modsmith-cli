"""Sphinx configuration for the command line's guide."""

from pathlib import Path
from typing import Any

from typer.main import get_command

import modsmith_app
from modsmith_app.cli.app import app as cli
from modsmith_app.core.config import SETTINGS
from modsmith_app.core.paths import HOME_VARIABLE

project = "Modsmith"
release = modsmith_app.__version__
author = "MeNeither"
copyright = "2026 MeNeither"

extensions = ["myst_parser", "modsmith_sphinx_theme"]
exclude_patterns = ["_build", "assets"]

html_theme = "modsmith"
html_title = project
html_baseurl = "https://modsmithmc.org/modsmith/"
html_theme_options = {
    "base_url": html_baseurl,
    "repository": "ModsmithMC/modsmith",
}
html_favicon = "assets/logo.svg"
html_static_path = ["assets"]
html_permalinks_icon = "#"
html_show_sourcelink = False
myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

modsmith_sections = {
    "get-started": "Get started",
    "guides": "Guides",
    "reference": "Reference",
    "help": "Help",
}

DOCS = Path(__file__).parent
COMMANDS = DOCS / "reference" / "commands"
TYPES = {"text": "text", "path": "path", "integer": "number", "boolean": ""}


def write(path: Path, text: str) -> None:
    """Write a generated page, leaving it untouched if nothing changed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def value_of(param: Any) -> str:
    """Describe what an option or argument takes, such as ``auto|always``."""
    if getattr(param, "is_flag", False) or getattr(param, "count", False):
        return ""
    choices = getattr(param.type, "choices", None)
    if choices:
        return "|".join(str(item) for item in choices)
    return TYPES.get(param.type.name, param.type.name)


def describe_param(param: Any) -> str:
    """Return one definition-list entry for an option or argument."""
    if param.param_type_name == "argument":
        name = param.name.upper()
        term = f"`{name}`" + (" ..." if param.nargs == -1 else "")
    else:
        names = ", ".join(f"`{item}`" for item in [*param.opts, *param.secondary_opts])
        kind = value_of(param)
        term = names + (f" *{kind}*" if kind else "")
    text = (param.help or "").strip()
    default = param.default
    shown = (
        param.param_type_name == "option"
        and not getattr(param, "is_flag", False)
        and default not in (None, (), [], 0, False, "")
    )
    if shown:
        text += f" Defaults to `{getattr(default, 'value', default)}`."
    if param.param_type_name == "argument" and not param.required:
        text += " Optional."
    return f"{term}\n: {text.strip()}\n"


def examples_of(command: Any) -> list[str]:
    """Return the example commands listed in a command's help."""
    epilog = command.epilog or ""
    return [line.strip() for line in epilog.splitlines() if line.startswith("  ")]


def usage_of(path: str, command: Any) -> str:
    """Write a command's usage line, such as ``modsmith add [OPTIONS] ITEMS ...``."""
    words = [path]
    if any(param.param_type_name == "option" for param in command.params):
        words.append("[OPTIONS]")
    for param in command.params:
        if param.param_type_name != "argument":
            continue
        name = param.name.upper()
        name = f"{name} ..." if param.nargs == -1 else name
        words.append(name if param.required else f"[{name}]")
    if hasattr(command, "commands"):
        words.append("COMMAND")
    return " ".join(words)


def command_page(path: str, command: Any) -> str:
    """Write the reference page of one command."""
    lines = [f"# {path}", "", (command.help or "").strip(), ""]
    lines += ["```console", f"$ {usage_of(path, command)}", "```", ""]
    arguments = [p for p in command.params if p.param_type_name == "argument"]
    options = [
        p
        for p in command.params
        if p.param_type_name == "option" and not p.hidden and p.name != "help"
    ]
    if arguments:
        lines += ["## Arguments", ""] + [describe_param(p) for p in arguments]
    if options:
        lines += ["## Options", ""] + [describe_param(p) for p in options]
    if hasattr(command, "commands"):
        lines += ["## Commands", ""]
        for name, sub in command.commands.items():
            lines.append(f"[`{path} {name}`]({slug(f'{path} {name}')}.md)")
            lines.append(f": {(sub.help or '').strip().splitlines()[0]}")
            lines.append("")
    examples = examples_of(command)
    if examples:
        lines += ["## Examples", "", "```console"]
        lines += [f"$ {item}" for item in examples]
        lines += ["```", ""]
    return "\n".join(lines)


def slug(path: str) -> str:
    """Name a command's page, such as ``config-set`` for ``modsmith config set``."""
    return path.removeprefix("modsmith ").replace(" ", "-")


def generate_reference() -> None:
    """Write a page for every command, and the settings page, from the code."""
    root = get_command(cli)
    entries: list[tuple[str, Any]] = []
    for name, command in root.commands.items():  # type: ignore[attr-defined]
        entries.append((f"modsmith {name}", command))
        for sub_name, sub in getattr(command, "commands", {}).items():
            entries.append((f"modsmith {name} {sub_name}", sub))
    for path, command in entries:
        write(COMMANDS / f"{slug(path)}.md", command_page(path, command))
    options = [
        p
        for p in root.params
        if p.param_type_name == "option" and not p.hidden and p.name != "help"
    ]
    index = [
        "# Commands",
        "",
        "Every command explains itself with `--help`. These pages show the same",
        "help, with examples.",
        "",
        "```{toctree}",
        ":hidden:",
        "",
        *[slug(path) for path, _ in entries],
        "```",
        "",
    ]
    for path, command in entries:
        if path.count(" ") > 1:
            continue
        summary = (command.help or "").strip().splitlines()[0]
        index += [f"[`{path}`]({slug(path)}.md)", f": {summary}", ""]
    index += [
        "## Options for every command",
        "",
        "These go before the command, as in `modsmith --verbose update`.",
        "",
    ]
    index += [describe_param(p) for p in options]
    write(COMMANDS / "index.md", "\n".join(index))

    rows = ["| Setting | What it does | Variable |", "| --- | --- | --- |"]
    for setting in SETTINGS.values():
        variable = f"`{setting.variable}`" if setting.variable else ""
        rows.append(f"| `{setting.key}` | {setting.description} | {variable} |")
    write(
        DOCS / "reference" / "settings.md",
        "\n".join(
            [
                "# Settings",
                "",
                "Settings live in `config.toml`. Change them with `modsmith config`:",
                "",
                "```console",
                "$ modsmith config",
                "$ modsmith config set default_platform curseforge",
                "$ modsmith config unset default_platform",
                "$ modsmith config path",
                "```",
                "",
                *rows,
                "",
                "An environment variable overrides the file, and a command line option",
                "such as `--instances-dir` overrides both, for that run only.",
                "",
                "## Other variables",
                "",
                f"`{HOME_VARIABLE}`",
                ": Keeps settings, instances and downloads together in this folder,",
                "  instead of your system's usual folders.",
                "",
                "`NO_COLOR`",
                ": Turns colour off, like `--color never`.",
                "",
            ]
        ),
    )


generate_reference()
