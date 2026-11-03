# Take over an existing installation

If you set up an installation in the official launcher yourself, Modsmith can
manage it in place.

## Prepare it

In the launcher, give the installation its own game directory, not the shared
`.minecraft` folder, and choose a fixed version rather than *Latest release*.
Start it once, so the launcher installs that version.

## Import it

```console
$ modsmith import "My Fabric world"
```

Name the installation as the launcher shows it. Modsmith reads which Minecraft
and mod loader it starts, turns its game directory into an instance, and
recognises the mods in it on Modrinth and on CurseForge if you set up a key.
Nothing is moved or downloaded.

The instance is named after its folder, and stays where it is. From then on,
`add`, `update`, `show` and the other commands work on it like on any other.

## Files you add by hand later

Run `adopt` to recognise them:

```console
$ modsmith adopt my-fabric-world
```
