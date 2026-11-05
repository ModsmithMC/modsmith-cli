# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Every pack gets its icon in the launcher. Icons are converted to the 128 by
  128 PNG the launcher shows. Before, WebP and GIF icons, and WebP icons
  labelled as PNG, were left out or did not show.
- New installations get memory to match: what the pack recommends, or half of
  the computer's memory up to 6 GB, always leaving a quarter for the computer.
  The launcher's own Java settings are kept. Before, a pack without a
  recommendation got the launcher's 2 GB, and one with a recommendation lost
  the launcher's other Java settings.
- CurseForge files whose authors turned off downloads through the API are
  downloaded from CurseForge's file server and checked against their hashes,
  with `install`, `add` and `update`. Before, each had to be downloaded by hand
  and passed with `--from`, which is now needed only for files CurseForge no
  longer lists.
- Packs for Forge 1.12.2 from 14.23.5.2851 install, and
  `modsmith loaders forge 1.12.2` lists those versions.

## [0.1.1] - 2026-11-04

### Added

- Modsmith is on PyPI as `modsmith-cli`: `uv tool install modsmith-cli`.
- A guide at [modsmithmc.org/modsmith-cli](https://modsmithmc.org/modsmith-cli/),
  with a page for every command and setting.

### Changed

- The project moved to [ModsmithMC/modsmith-cli](https://github.com/ModsmithMC/modsmith-cli).
- The package is now called `modsmith-cli`; the command is still `modsmith`.
  If you installed 0.1.0 from its wheel, remove it first with
  `uv tool uninstall modsmith-app` (or `pipx uninstall modsmith-app`). Your
  instances and settings stay where they are.
- The Python package is `modsmith_cli`, so `python -m modsmith_cli` runs it.

## [0.1.0] - 2026-11-03

The first release of the `modsmith` command.

### Added

- `list`, `search` and `config`.
- Settings in `config.toml`, overridden by environment variables and command
  line options. `MODSMITH_HOME` keeps everything in one folder.
- `install` installs a modpack, from a file, Modrinth or CurseForge, as a new
  instance with its own installation in the official launcher. It shows what it
  will change and asks first, lets you choose optional files, and takes files
  you downloaded by hand with `--from`.
- `create` starts an empty instance, with the recommended version of a mod
  loader unless you name one.
- `show` lists what an instance holds and where each file came from. `add`
  adds mods, resource packs and shaders with what they need, and `remove`
  takes them away with the dependencies nothing else needs. `enable`,
  `disable`, `pin`, `unpin` and `adopt` manage what is there.
- `update` updates an instance's pack, keeping the optional files you chose,
  and the projects you added, showing what changed in each release. A pack
  installed from a file updates with `--file`.
- `import` turns an installation you made in the official launcher into an
  instance, reading its Minecraft and loader versions and recognising its mods.
- `move` renames an instance or moves its folder, and `delete` deletes it after
  you type its name. Both keep the launcher installation in step.
- `info` shows a project's details, newest releases and changelog, and
  `loaders` lists a mod loader's versions.
- `search --sort` orders results by relevance, downloads, popularity, newest or
  last update.
- `--color` and `NO_COLOR` control colour. Help shows examples.
- Errors name every file that failed to download, and where to get files that
  must be downloaded by hand.
