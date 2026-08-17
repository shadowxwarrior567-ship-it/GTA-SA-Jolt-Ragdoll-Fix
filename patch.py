#!/usr/bin/env python3
"""
Buggy Ragdoll v3.10 - Patch B
Recovery-state synchronization candidate.

Input:
    libBuggyRagdoll.so

Output:
    libBuggyRagdoll_patchB.so

This changes ONE Thumb-2 instruction in the recovery path:

    0x7510c:
        strb.w r6, [r8, #0x5]

to:

        strh.w r6, [r8, #0x4]

Because r6 is zero here, this clears the two adjacent state bytes
at +0x04 and +0x05 together when recovery completes.

Why:
    The normal recovery path clears +0x05 but leaves +0x04 set.
    Both bytes are used by the ragdoll table as state gates:
      +0x04 = table entry active
      +0x05 = ragdoll/HAnim active

Patch B makes the recovery transition atomic from the table's point
of view. It does NOT claim to create a stand-up animation by itself.
The existing animation system still has to choose the post-ragdoll
animation.

This deliberately does not touch:
    - Jolt constants
    - ground sampling
    - bone constraints
    - vehicle code
"""

from pathlib import Path
import sys

INPUT = Path("libBuggyRagdoll.so")
OUTPUT = Path("libBuggyRagdoll_patchB.so")

# ELF .text has identical virtual address and file offset in this build.
PATCH_VA = 0x7510C
PATCH_FILE_OFFSET = 0x7510C

# Existing instruction:
#   f8 88 60 05  (Thumb-2: strb.w r6,[r8,#5])
OLD = bytes.fromhex("f8 88 60 05")

# New instruction:
#   f8 a8 60 04  (Thumb-2: strh.w r6,[r8,#4])
NEW = bytes.fromhex("f8 a8 60 04")


def main():
    if not INPUT.exists():
        print("ERROR: libBuggyRagdoll.so was not found.")
        sys.exit(1)

    data = bytearray(INPUT.read_bytes())

    if PATCH_FILE_OFFSET + 4 > len(data):
        print("ERROR: patch offset is outside the file.")
        sys.exit(1)

    current = bytes(data[PATCH_FILE_OFFSET:PATCH_FILE_OFFSET + 4])

    print(f"Recovery patch address: 0x{PATCH_VA:08X}")
    print(f"Current bytes: {current.hex(' ')}")
    print(f"Expected:      {OLD.hex(' ')}")

    if current != OLD:
        print()
        print("ERROR: The binary does not match the expected v3.10")
        print("recovery instruction. Refusing to patch.")
        sys.exit(2)

    data[PATCH_FILE_OFFSET:PATCH_FILE_OFFSET + 4] = NEW
    OUTPUT.write_bytes(data)

    print()
    print("Patch B applied successfully.")
    print(f"Created: {OUTPUT}")
    print()
    print("Changed:")
    print("  strb.w r6,[r8,#5]")
    print("to:")
    print("  strh.w r6,[r8,#4]")
    print()
    print("The original library was not modified.")


if __name__ == "__main__":
    main()
