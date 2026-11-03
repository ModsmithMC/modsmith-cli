# Questions people ask

## Is Modsmith a launcher?

No. It prepares the game files and adds an installation to the official
launcher, then the launcher does the rest: signing in, starting the game and
keeping Minecraft itself up to date.

## Do I need an account, or a CurseForge key?

You need a Minecraft account in the official launcher, as always. Modsmith
itself needs none. Modrinth works straight away; CurseForge needs a free
[API key](../guides/curseforge.md).

## Will it touch my other installations?

No. Modsmith changes only the instances and launcher installations it made, or
the ones you [import](../guides/existing.md).

## Can I still change settings and add files by hand?

Yes. Files you edit are kept when you update. Files you add yourself stay as
they are; `modsmith adopt` can take them over so they update too.

## Why did an update keep an old config file?

Because you changed it. Modsmith keeps your version and marks it with `!` in the
plan. Use `--overwrite` to take the pack's new version instead.

## Why does it say a project has no release for my instance?

The project has no release for that Minecraft version and mod loader, or only
alpha and beta releases. `modsmith info <project>` lists its releases; `--pre`
allows test releases.

## Where are my worlds?

In the instance's `saves` folder. Find the instance with `modsmith list`.
`modsmith delete` says how many worlds it holds before it deletes anything.

## Can I move my instances to another drive?

Yes: `modsmith move <name> D:/Games/<name>`. The launcher installation follows.
To put new instances there too, see [where things go](../concepts/instances.md#where-things-go).

## How do I uninstall Modsmith?

`uv tool uninstall modsmith-cli`. Instances and their launcher installations
stay; delete those first with `modsmith delete` if you want them gone too.
