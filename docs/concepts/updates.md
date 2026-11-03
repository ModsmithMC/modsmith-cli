# How changes stay safe

Everything that changes files follows the same steps, whether it installs a
pack, adds a mod or updates.

## 1. You see it first

Modsmith lists every file it will add (`+`), update (`~`) or remove (`-`), and
the download size, then asks. Add `--dry-run` to see the list and stop there.
Add `--yes` to skip the question.

## 2. It checks before it changes anything

Everything a pack or mod needs is looked up first. A missing dependency, a
conflict, or a file that must be downloaded by hand stops it before any file
changes.

## 3. It downloads to the side

New files are downloaded and checked in a separate folder, so a dropped
connection or Ctrl+C leaves the instance as it was. Run the same command again
to carry on; what was already downloaded is used.

## 4. It swaps the files in

Only then are the new files moved into place. If anything fails while moving,
the old files go back.

## Your edits are kept

Modsmith remembers what each file looked like when it put it there. If you
changed one since, such as a config file, an update keeps your version and
says so with `!`. Removing a mod keeps a file you changed in the same way. Use
`--overwrite` when you do want the new version.
