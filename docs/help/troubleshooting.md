# Troubleshooting

## "Close the official launcher first."

A running launcher can write over its list of installations, and lose the one
Modsmith adds. Close it, run the command again, then open it.

## "This command changes files and there is no terminal to confirm in."

Modsmith never asks a question it cannot show. When its input does not come from
a terminal, as in a script or a pipe, add `--yes` to go ahead. Deleting also
needs `--force`.

## "CurseForge rejected the API key."

Set the key again. In PowerShell, use single quotes around it, because a `$`
inside double quotes starts a variable:

```console
$ modsmith config set curseforge_api_key '<key>'
```

## Files that cannot be downloaded automatically

The platform no longer lists them, so they have to come from you. Put each
listed file into one folder, and add `--from <folder>`. See
[Use CurseForge](../guides/curseforge.md#files-you-must-download-by-hand).

## "... has no release for this instance"

The project has no release for the instance's Minecraft version and mod loader,
or only alpha and beta releases. Check with `modsmith info <project>`, and add
`--pre` to allow test releases.

## "Nothing in ... is called ..."

`enable` and `disable` look for a project you added, a file name, or the name a
mod gives itself. Run `modsmith show <instance>` to see what is there.

## "Not added on its own"

Files from the pack cannot be removed or pinned on their own; they follow the
pack. You can turn them off with `modsmith disable`.

## "There is no Minecraft ..."

Check the version, such as `1.21.1`. Snapshots work too.

## Question marks in piped output

When you pipe or redirect Modsmith's output, it is written in your system's code
page, so the shell reads it correctly. Characters that code page lacks, such as
emoji in a pack's name, are written as `?`.

## See more detail

Add `-v` before the command to see what Modsmith does, and `-vv` for everything:

```console
$ modsmith -v update fo
```
