# Buggy Ragdoll v3.10 — All-in-One Experimental Patch

This build combines the configuration changes we have been testing with the
verified recovery-state byte patch.

## Targets

- ordinary jump accidentally entering ragdoll
- recovery taking too long / failing to leave the physics state
- excessive bone drift / stretching
- aggressive anchor/motor correction
- preserve the known-good ground settings

## Important

This is an **experimental test build**, not a guaranteed final fix.

The jump trigger is addressed by raising the existing impact/fall thresholds.
The recovery path is given more time and a softer blend, plus the recovery
state candidate clears both adjacent state bytes.

The ground settings remain:

- GroundSamples = 15
- GroundExtent = 4.5
- RebuildDist = 0.60

## Files

Place:

    libBuggyRagdoll.so
    patch.py

in the same directory and run:

    python3 patch.py

It creates:

    libBuggyRagdoll_allfix_test.so

The original library is never modified.

## Test order

1. Start the game and walk normally.
2. Jump repeatedly.
   - A normal jump should NOT ragdoll.
3. Cause a small fall.
4. Cause a hard impact.
5. Trigger ragdoll and wait.
6. Test CJ and NPC recovery separately.
7. Test CJ weapons while ragdolled.
8. Test vehicle impacts / entering / exiting vehicles.
9. Check limb stretching.
10. Confirm the ground fix is still good.
11. Confirm there are no crashes.

If normal jumping is fixed but recovery is still broken, do not keep changing
random constants. That result means the remaining recovery problem is the
GTA animation-task handoff and needs a code-path patch.
