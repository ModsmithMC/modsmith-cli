# Use CurseForge

Modrinth works straight away. CurseForge needs an API key, which is free.

## Set up a key

1. Sign in to the [CurseForge console](https://console.curseforge.com) and
   create an API key.
2. Save it:

   ```console
   $ modsmith config set curseforge_api_key '<key>'
   ```

In PowerShell, keep the single quotes. Keys contain `$`, and inside double
quotes PowerShell treats it as the start of a variable. If CurseForge rejects
the key, set it again this way.

You can also set the `CURSEFORGE_API_KEY` environment variable instead.

## Name CurseForge projects

Put `curseforge:` in front of a name, or use the project's address:

```console
$ modsmith search jei --platform curseforge
$ modsmith add fo curseforge:jei
$ modsmith install https://www.curseforge.com/minecraft/modpacks/all-the-mods-9
```

To make CurseForge the default, run
`modsmith config set default_platform curseforge`.

## Files you must download by hand

Some authors do not allow other tools to download their files. Modsmith lists
each such file with the page to get it from:

```text
Error: 1 file cannot be downloaded automatically.
  mods/entityculling-fabric-1.11.3-mc26.2.jar  download it from https://www.curseforge.com/minecraft/mc-mods/entityculling/files/9100313
Download them by hand into one folder, then run the command again with --from <folder>.
```

Download them into one folder, keeping their names, and add `--from`:

```console
$ modsmith install curseforge:fabulously-optimized --from Downloads/manual
```

`--from` works the same with `add` and `update`. With `--dry-run`, Modsmith
shows the plan and lists the files to download, without stopping.
