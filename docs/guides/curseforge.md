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

## Files other tools may not download

Some authors turn off downloads of their files through CurseForge's API.
CurseForge still serves those files to its own app, so Modsmith downloads them
the same way and checks each one against the hashes CurseForge lists. You do
not need to do anything.

## Files you must download by hand

A file that CurseForge no longer lists cannot be downloaded at all. Modsmith
names each such file:

```text
Error: 1 file cannot be downloaded automatically.
  curseforge file 9100313
Download them by hand into one folder, then run the command again with --from <folder>.
```

Find them, put them into one folder with their names, and add `--from`:

```console
$ modsmith install curseforge:some-pack --from Downloads/manual
```

`--from` works the same with `add` and `update`. With `--dry-run`, Modsmith
shows the plan and lists the files to download, without stopping.
