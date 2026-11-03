# Manage instances

An instance is a folder that holds a game's mods, settings and worlds, with an
installation in the official launcher that plays from it.

## List them

```console
$ modsmith list
```

Most commands take the instance's name first. When you have only one, you can
leave it out.

## Start from nothing

```console
$ modsmith loaders fabric 1.21.1
$ modsmith create survival --minecraft 1.21.1 --loader fabric
$ modsmith add survival sodium lithium
```

`create` installs Minecraft and the mod loader, and adds the launcher
installation. Without `--loader-version`, it uses the loader's recommended
version. Without `--loader`, the instance plays plain Minecraft.

## Rename or move

```console
$ modsmith move survival creative
$ modsmith move creative D:/Games/creative
```

A new name keeps the instance in the folder it is in. A path moves it there.
The launcher installation follows.

## Delete

```console
$ modsmith delete creative
```

This deletes the instance's folder, worlds included, and its launcher
installation. Modsmith says how many worlds it holds, and asks you to type the
name. Without a terminal, it needs both `--yes` and `--force`.

## Where things go

| What | Where |
| --- | --- |
| Instances | Your user data folder, under `Modsmith/instances` (`modsmith/instances` on Linux) |
| Settings | `config.toml`; `modsmith config path` prints where |
| Downloads | Your user cache folder, under `Modsmith` |
| Minecraft and mod loaders | The official launcher's game folder |
| Launcher installations | The launcher's `launcher_profiles.json`, one per instance |

Change where new instances go with
`modsmith config set instances_dir <folder>`. Set `MODSMITH_HOME` to keep
settings, instances and downloads in one folder. See [settings](../reference/settings.md).
