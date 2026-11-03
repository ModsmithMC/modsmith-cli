# Instances and the launcher

## An instance

An instance is a folder that holds one game's mods, resource packs, shaders,
settings and worlds. Each instance plays one Minecraft version with one mod
loader, or none.

Keeping each game in its own folder means a modpack's mods never mix with
another's, and deleting one leaves the others as they are.

## Its installation in the launcher

For every instance, Modsmith adds an *installation* to the official launcher:
the entries you choose from before pressing Play. It points the launcher at the
instance's folder and at the right Minecraft version and mod loader, and uses
the pack's name and icon.

Modsmith changes only the installations it added. Your own stay as they are,
unless you [import](../guides/existing.md) one.

## Minecraft and mod loaders

Minecraft versions and mod loaders are shared. Modsmith installs them where the
official launcher keeps its own, in its game folder, so two instances on the
same version share one copy.

## Naming an instance

Commands take the instance's name first, as in `modsmith add survival sodium`.
When you have only one instance, you can leave its name out. Names are the
folder's name, and complete when you press Tab.

## Where things go

| What | Where |
| --- | --- |
| Instances | Your user data folder, under `Modsmith/instances` (`modsmith/instances` on Linux) |
| Settings | `config.toml`; `modsmith config path` prints where |
| Downloads | Your user cache folder, under `Modsmith`; safe to delete |
| Minecraft and mod loaders | The official launcher's game folder |
| Launcher installations | The launcher's `launcher_profiles.json`, one per instance |

Change where new instances go with
`modsmith config set instances_dir <folder>`. Set `MODSMITH_HOME` to keep
settings, instances and downloads in one folder. See
[settings](../reference/settings.md).
