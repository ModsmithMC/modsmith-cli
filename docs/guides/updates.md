# Keep instances up to date

```console
$ modsmith update fo
```

`update` looks for a newer release of the instance's pack, and of everything you
added, then shows what will change and what changed in each release, and asks.

## What stays

- Files you edited, such as a changed config, are kept. Use `--overwrite` to
  replace them with the new versions.
- Files you turned off stay off.
- Optional pack files you chose stay chosen. If a new release drops one, Modsmith
  says so.
- Pinned projects stay at their release.

## Preview first

```console
$ modsmith update fo --dry-run
```

## Only part of it

```console
$ modsmith update fo --pack-only
$ modsmith update fo --additions-only
```

## A new Minecraft version

When a new pack release moves to another Minecraft version or mod loader,
Modsmith installs it and points the launcher installation at it. What you
added is updated the next time you run `update`, against the new version.

## Packs installed from a file

A pack installed from a file cannot look for new releases on its own. Give it
the newer file:

```console
$ modsmith update atm9 --file Downloads/atm9-1.2.zip
```

## Choose optional files again

```console
$ modsmith update fo --optional shaders
$ modsmith update fo --all-optional
```

## Alpha and beta releases

Add `--pre`, or allow them always with
`modsmith config set allow_prereleases true`.
