from pathlib import Path
import sys

INPUT = Path("libBuggyRagdoll.so")
OUTPUT = Path("libBuggyRagdoll_patchB.so")

PATCH_OFFSET = 0x7510C

# Actual bytes found in your library.
OLD = bytes.fromhex("88 f8 05 60")

# Replacement for:
#   strh.w r6, [r8, #4]
NEW = bytes.fromhex("a8 f8 04 60")

if not INPUT.exists():
    print("ERROR: libBuggyRagdoll.so was not found.")
    sys.exit(1)

data = bytearray(INPUT.read_bytes())

if PATCH_OFFSET + 4 > len(data):
    print("ERROR: patch offset is outside the file.")
    sys.exit(1)

current = bytes(data[PATCH_OFFSET:PATCH_OFFSET + 4])

print(f"Recovery patch address: 0x{PATCH_OFFSET:08X}")
print(f"Current bytes: {current.hex(' ')}")
print(f"Expected:      {OLD.hex(' ')}")

if current != OLD:
    print("ERROR: Binary does not match the expected library.")
    print("Refusing to patch.")
    sys.exit(2)

data[PATCH_OFFSET:PATCH_OFFSET + 4] = NEW

OUTPUT.write_bytes(data)

print()
print("Patch B applied successfully.")
print(f"Created: {OUTPUT}")
print(f"Changed: {OLD.hex(' ')} -> {NEW.hex(' ')}")
