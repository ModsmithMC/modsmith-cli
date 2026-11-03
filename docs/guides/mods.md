# Add mods, resource packs and shaders

Anything you add to an instance is kept apart from its pack, so it can be
updated and removed on its own, and pack updates leave it alone.

## Add

Name the instance, then what to add:

```console
$ modsmith add fo iris sodium-extra
$ modsmith add fo curseforge:jei
$ modsmith add fo faithful-32x --type resourcepack
$ modsmith add fo complementary-reimagined --type shader
```

Modsmith picks each project's newest release for the instance's Minecraft
version and mod loader, and the mods it needs come along. The plan says which
ones came as dependencies, which projects are already in the pack, and which
have no release for this instance. Add `--optional` to bring optional
dependencies too, and `--pre` to allow alpha and beta releases.

A mod's dependency with no full release at all, such as a new library, is
installed from its newest beta, since the mod cannot work without it.

## See what an instance holds

```console
$ modsmith show fo
```

Each file is listed with its name and version, and where it came from: **pack**,
**added**, or **yours** for files you put there yourself. Files that are off or
pinned are marked.

## Turn files off

`disable` keeps a file but stops the game loading it. It works on anything,
including files from the pack:

```console
$ modsmith disable fo iris
$ modsmith enable fo iris
```

Name a file by its project, its file name, or the name the mod gives itself.
Updates keep disabled files disabled.

## Remove

```console
$ modsmith remove fo iris --dry-run
$ modsmith remove fo iris
```

Removing a project also removes the dependencies that nothing else needs. Keep
them with `--keep-deps`. Files you changed are kept and listed. Only what you
added can be removed; to stop the game loading a pack file, disable it.

## Pin a version

```console
$ modsmith pin fo iris
$ modsmith unpin fo iris
```

A pinned project stays at its release when you update.

## Files you put there yourself

If you copied mods into an instance by hand, Modsmith can recognise them on
Modrinth and CurseForge, so they can be updated and removed like added ones:

```console
$ modsmith adopt fo
```

Files it cannot recognise stay as they are.
