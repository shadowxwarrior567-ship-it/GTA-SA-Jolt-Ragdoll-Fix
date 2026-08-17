# Buggy Ragdoll v3.10 - Stability Fix

This project patches the existing Buggy Ragdoll v3.10
Jolt Physics library.

It does NOT replace the Jolt physics engine.

## Target

- GTA San Andreas 2.00
- Android
- ARMv7 / armeabi-v7a
- AML
- Buggy Ragdoll v3.10

## Approach

The original library contains the complete Jolt ragdoll
implementation.

This project modifies its exported physics/stability
configuration values while leaving the original physics
implementation intact.

## Main goals

- reduce bone stretching
- reduce excessive joint correction
- improve root/anchor stability
- improve ground behavior
- reduce jitter
- improve ragdoll recovery
- reduce excessive drift

## Testing

The original library must be kept as a backup.

The generated file is:

libBuggyRagdoll_fixed.so

Do not overwrite the original until the patched version
has been tested.

## Rollback

If the game crashes or behaves worse, restore the original
libBuggyRagdoll.so.
