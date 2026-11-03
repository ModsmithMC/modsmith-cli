# Install modpacks

`install` turns a modpack into an instance: a folder with the pack's files, and
an installation in the official launcher that plays it.

## From Modrinth, CurseForge or a file

```console
$ modsmith install fabulously-optimized
$ modsmith install curseforge:all-the-mods-9
$ modsmith install https://modrinth.com/modpack/fabulously-optimized
$ modsmith install Downloads/my-pack.mrpack
```

A bare name is looked up on Modrinth, unless you
[change the default platform](../reference/settings.md). CurseForge needs a
key first; see [Use CurseForge](curseforge.md).

From a platform, Modsmith installs the pack's newest full release. To allow
alpha and beta releases, run
`modsmith config set allow_prereleases true`.

## What it does

1. Downloads the pack and reads it.
2. Shows every file it will add, with the download size, and asks.
3. Installs the pack's Minecraft version and mod loader into the launcher's game
   folder.
4. Puts the pack's files into a new instance folder.
5. Adds an installation to the launcher, with the pack's name and icon, playing
   from that folder.

To see the plan without changing anything, add `--dry-run`. To skip the
question, add `--yes`.

## Name the instance

The instance is named after the pack, such as `fabulously-optimized`. Choose a
shorter name with `--name`:

```console
$ modsmith install fabulously-optimized --name fo
```

Names may use letters, digits, spaces, dots, dashes and underscores. If you
install the same pack twice, the second launcher installation is told apart by
its instance name, as in *Fabulously Optimized (fo2)*.

## Optional files

Some packs offer optional files, such as extra shaders. Modsmith asks which
ones you want. To decide on the command line, name them, or take them all:

```console
$ modsmith install fabulously-optimized --optional shaders --optional zoom
$ modsmith install fabulously-optimized --all-optional
```

`--optional` takes part of a file's name, and can be repeated. Without a
terminal to ask in, optional files are left out, and Modsmith says so. Your
choice is remembered for [updates](updates.md).

## Files you must download by hand

Some CurseForge authors do not allow other tools to download their files. Then
Modsmith lists those files, each with the page to get it from. Download them
into one folder, and run the command again with `--from`:

```console
$ modsmith install curseforge:all-the-mods-9 --from Downloads/atm9-files
```

Modsmith finds each file by its name and checks that it is the right one.

## Start without a pack

To start an empty instance and add mods yourself, see
[Manage instances](instances.md#start-from-nothing).
