# Quick start

This installs a modpack, adds a mod to it and keeps it up to date.

## Find a modpack

```console
$ modsmith search optimized --type modpack --sort downloads
```

The **Use as** column shows the name to give other commands, such as
`fabulously-optimized`. Look at a project more closely with `info`:

```console
$ modsmith info fabulously-optimized --type modpack
```

## Install it

```console
$ modsmith install fabulously-optimized --name fo
```

Modsmith shows what it will install and asks first. It downloads the pack, its
mod loader and Minecraft, and adds an installation called Fabulously Optimized
to the official launcher. `fo` is the name you use for it in Modsmith.

Open the launcher, choose the installation and play.

## Add to it

```console
$ modsmith add fo iris
$ modsmith add fo complementary-reimagined --type shader
$ modsmith show fo
```

Mods that Iris needs come along. `show` lists every file and where it came
from: the pack, something you added, or a file you put there yourself.

## Keep it up to date

```console
$ modsmith update fo
```

This updates the pack and what you added, and shows what changed in each
release. Files you edited stay as they are.

## Leave out the name

When you have only one instance, you can leave its name out:

```console
$ modsmith update
```

## Next

- [Install modpacks](../guides/modpacks.md) from CurseForge or a file, and
  choose optional files.
- [Add mods](../guides/mods.md), turn them off, and pin their versions.
- See every command in the [reference](../reference/commands/index.md).
