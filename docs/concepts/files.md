# Where files come from

Every mod, resource pack and shader in an instance came from one of three
places. `modsmith show` lists them:

| Source | What it means | What Modsmith does with it |
| --- | --- | --- |
| **pack** | The modpack installed it | Updates it with the pack. You can turn it off, but not remove it on its own |
| **added** | You added it with `modsmith add` | Updates, pins and removes it, with the mods it needs |
| **yours** | You put it there yourself | Leaves it alone, until you `adopt` it |

## Added projects and their dependencies

When you add a mod, the mods it needs come along. Modsmith remembers which ones
you asked for and which came as dependencies, so removing a mod also removes
the dependencies nothing else needs.

If the pack already has a project you add, Modsmith says so, and the pack's copy
stays in charge.

## Pinned projects

A pinned project stays at its release when you update. Pin a mod when a newer
release breaks something, and unpin it when that is fixed.

## Adopting your own files

Files you copied in by hand are **yours**. `modsmith adopt` looks them up on
Modrinth and CurseForge by their contents. Those it recognises become
**added**, so they can be updated and removed. The rest stay as they are.

## Files that are off

A file turned off with `modsmith disable` stays in place with `.disabled` at the
end of its name, so the game skips it. Updates keep it off.
