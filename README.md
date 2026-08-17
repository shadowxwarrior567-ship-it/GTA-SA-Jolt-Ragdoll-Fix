# Buggy Ragdoll v3.10 — Patch B

This is the first targeted recovery-state synchronization patch.

## What it changes

At the recovery path, v3.10 currently clears only the state byte at:

    entry + 0x05

while the table-active byte at:

    entry + 0x04

remains set until later cleanup.

Patch B changes that single instruction so recovery clears both adjacent
bytes atomically.

## What this is NOT

This is not a guaranteed "make CJ stand up" patch.

The existing binary does not expose a safe, named GTA animation-task function
for us to call from this location. Patch B therefore does not invent a
hard-coded game address.

It targets only the state transition that we can verify from the ARM code.

## Build

Put the ORIGINAL v3.10 `libBuggyRagdoll.so` beside `patch.py` and run:

    python3 patch.py

Output:

    libBuggyRagdoll_patchB.so

Keep the original and your previously successful fixed library as backups.

## Test

Test CJ and NPC separately:

1. Trigger ragdoll.
2. Wait without pressing anything.
3. Check whether the ragdoll ends cleanly.
4. Check whether the ped returns to a normal animation.
5. Check whether CJ can still use weapons during ragdoll.
6. Check stretching and ground behavior.
7. Check vehicle impacts.
8. Confirm no crashes.

If recovery is still stuck, that tells us Patch B's state cleanup is not the
missing piece and we should move to the actual animation-task handoff rather
than changing more physics constants.
