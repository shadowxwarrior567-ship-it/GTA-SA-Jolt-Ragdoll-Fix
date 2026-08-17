# Buggy Ragdoll Mega Test

This combines the currently verified experimental fixes into one test build.

### Included

1. Normal-jump trigger filtering.
2. Reduced excessive impact/fall sensitivity.
3. Reduced visible bone stretching.
4. Existing ground/foot fixes retained.
5. Recovery-state synchronization test.
6. Damage-event ragdoll bypass, targeting the reported gunshot problem.
7. Vehicle/run-over path left intact.

### Save/load location issue

The reported bug where loading a save can put CJ at his last runtime position
instead of the safehouse/save location is included in the investigation, but
is NOT blindly binary-patched in this build.

The available evidence shows `PedProcessControl` and `FindPlayerPed` are involved,
but the supplied disassembly does not safely identify the exact instruction
responsible for writing/overriding CJ's saved position. Disabling the whole hook
would risk breaking ragdoll and/or crashing.

So this build intentionally leaves that behavior untouched while combining
everything else. This gives a clean test result:

- If all ragdoll/damage issues improve but save/load remains wrong, the save
  bug is isolated to the player-position hook.
- If save/load becomes correct by itself, no additional position patch is needed.

## Test checklist

1. Walk.
2. Jump 10 times.
3. Shoot CJ.
4. Shoot NPC.
5. Hard impact.
6. Vehicle/run-over.
7. Wait for recovery.
8. Try weapons during ragdoll.
9. Check stretching.
10. Check feet/ground.
11. Save at a safehouse.
12. Walk a substantial distance away.
13. Reload that save.
14. Verify CJ appears at the safehouse/save location.
15. Check for crashes.

Keep the original `libBuggyRagdoll.so` as a backup.
