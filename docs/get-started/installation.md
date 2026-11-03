# Installation

Modsmith runs on Windows, macOS and Linux. It is installed with
[uv](https://docs.astral.sh/uv/), which also brings the Python it needs, so
you do not have to install Python yourself.

## Install

```{raw} html
<div class="tabs" data-tabs>
  <div class="tab-list" role="tablist">
    <button type="button" role="tab" data-tab="windows">Windows</button>
    <button type="button" role="tab" data-tab="macos">macOS</button>
    <button type="button" role="tab" data-tab="linux">Linux</button>
  </div>
  <div class="tab-panel" role="tabpanel" data-panel="windows">
```

1. Install uv. In PowerShell:

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. Open a new PowerShell window, and install Modsmith:

   ```powershell
   uv tool install modsmith-cli
   ```

```{raw} html
  </div>
  <div class="tab-panel" role="tabpanel" data-panel="macos" hidden>
```

1. Install uv. In Terminal:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Open a new Terminal window, and install Modsmith:

   ```bash
   uv tool install modsmith-cli
   ```

```{raw} html
  </div>
  <div class="tab-panel" role="tabpanel" data-panel="linux" hidden>
```

1. Install uv:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Open a new terminal, and install Modsmith:

   ```bash
   uv tool install modsmith-cli
   ```

```{raw} html
  </div>
</div>
```

Already use [pipx](https://pipx.pypa.io/)? `pipx install modsmith-cli` works
too.

## Check that it works

```console
$ modsmith --version
modsmith 0.1.0
```

If the terminal says it does not know `modsmith`, open a new one, so it picks
up the folder uv installed it to.

## Before your first modpack

Modsmith works with the official Minecraft launcher. Install it, sign in, and
start it once, so that it creates its game folder. Close it while Modsmith adds,
moves or removes installations; Modsmith checks, and asks you to.

## Tab completion

Modsmith can complete commands and instance names when you press Tab:

```console
$ modsmith --install-completion
```

Then open a new terminal.

## Upgrade

```console
$ uv tool upgrade modsmith-cli
```

## Uninstall

```console
$ uv tool uninstall modsmith-cli
```

Your instances and settings stay where they are. To remove them too, see
[where things go](../concepts/instances.md#where-things-go).

## Next

[Install your first modpack](quickstart.md).
