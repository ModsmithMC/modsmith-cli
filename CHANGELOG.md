# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- A guide at [modsmithmc.org/modsmith](https://modsmithmc.org/modsmith/),
  with a page for every command and setting.

### Changed

- The project moved to [ModsmithMC/modsmith](https://github.com/ModsmithMC/modsmith).

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
