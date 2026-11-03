# Changelog

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The `modsmith` command, with `list`, `search` and `config`.
- Settings in `config.toml`, overridden by environment variables and command
  line options. `MODSMITH_HOME` keeps everything in one folder.
- `install` installs a modpack, from a file, Modrinth or CurseForge, as a new
  instance with its own installation in the official launcher. It shows what it
  will change and asks first, lets you choose optional files, and takes files
  you downloaded by hand with `--from`.
- `create` starts an empty instance, with the recommended version of a mod
  loader unless you name one.
- `search --sort` orders results by relevance, downloads, popularity, newest or
  last update.
- `--color` and `NO_COLOR` control colour. Help shows examples.
- Errors name every file that failed to download, and where to get files that
  must be downloaded by hand.
