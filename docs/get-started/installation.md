# Installation

Modsmith runs on Windows, macOS and Linux, and needs Python 3.12 or newer.

## Install

Install it as a tool with [uv](https://docs.astral.sh/uv/), from the
[latest release](https://github.com/ModsmithMC/modsmith/releases/latest):

```console
$ uv tool install https://github.com/ModsmithMC/modsmith/releases/download/v0.1.0/modsmith_app-0.1.0-py3-none-any.whl
```

Or with [pipx](https://pipx.pypa.io/):

```console
$ pipx install https://github.com/ModsmithMC/modsmith/releases/download/v0.1.0/modsmith_app-0.1.0-py3-none-any.whl
```

Both put the `modsmith` command on your path, in its own environment. Check
that it works:

```console
$ modsmith --version
modsmith 0.1.0
```

## Before you start

Modsmith works with the official Minecraft launcher, and expects it to be set
up: install it, sign in and start it once, so that it creates its game folder.
Close it while Modsmith adds, moves or removes installations, because a running
launcher can write over its list of installations. Modsmith checks, and asks you
to close it.

## Tab completion

Modsmith can complete commands and instance names when you press Tab:

```console
$ modsmith --install-completion
```

Open a new terminal afterwards.

## Upgrade and uninstall

To move to a newer release, install its file the same way. To remove
Modsmith:

```console
$ uv tool uninstall modsmith-app
```

Your instances and settings stay where they are. See
[where things go](../guides/instances.md#where-things-go) to remove them too.
