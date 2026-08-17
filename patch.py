#!/usr/bin/env python3
import struct
import sys
from pathlib import Path

INPUT = Path("libBuggyRagdoll.so")
OUTPUT = Path("libBuggyRagdoll_allfix_test.so")

# These addresses are from the supplied GTA SA Android ARMv7
# Buggy Ragdoll v3.10 library.
DATA_VADDR = 0x00193BA8
DATA_OFFSET = 0x00191BA8

GLOBALS = {
    "gMaxRagdollTime": 0x00193BC4,
    "gBlendTime":      0x00193BBC,
    "gRecoverTime":    0x00193BC0,
    "gGravity":        0x00193BCC,
    "gTeleportVel":    0x00193BD0,
    "gImpactDeltaV":   0x00193BD4,
    "gFallSpeed":      0x00193BD8,
    "gAnchorBlend":    0x00193BE4,
    "gAnchorGain":     0x00193BE8,
    "gSnapDist":       0x00193BEC,
    "gTearDownDist":   0x00193BF0,
    "gMaxBoneDrift":   0x00193BF4,
    "gMotorFreq":      0x00193BF8,
    "gMotorDamp":      0x00193BFC,
    "gTorqueSpine":    0x00193C00,
    "gTorqueLimb":     0x00193C04,
    "gTorqueNeck":     0x00193C08,
    "gGravComp":       0x00193C0C,
    "gFootLength":     0x00193C10,
    "gFootBalanceAmt": 0x00193C14,
    "gMaxAngle":       0x00193C18,
    "gSpinThreshold":  0x00193C1C,
    "gStepPredictFwd": 0x00193C20,
    "gStepPredictBack":0x00193C24,
    "gMaxStepLength":  0x00193C28,
    "gStepHeight":     0x00193C2C,
    "gBraceTime":      0x00193C30,
    "gGiveUpTime":     0x00193C34,
    "gWindmillAmount": 0x00193C38,
    "gLocoDamp":       0x00193C3C,
    "gGroundSamples":  0x00193C40,
    "gGroundExtent":   0x00193C44,
    "gRebuildDist":    0x00193C48,
}

# Combined test preset:
# - raise fall/impact thresholds so an ordinary jump is less likely to
#   enter ragdoll;
# - give the existing recovery system more time and a softer blend;
# - reduce aggressive motor/anchor correction that can fight recovery;
# - tighten bone drift to reduce visible stretching;
# - preserve the already successful ground settings.
CONFIG = {
    "gMaxRagdollTime": 4.50,
    "gBlendTime": 0.30,
    "gRecoverTime": 1.50,
    "gGravity": -9.81,
    "gTeleportVel": 25.0,

    # Trigger filtering:
    "gImpactDeltaV": 10.0,
    "gFallSpeed": 6.50,

    "gAnchorBlend": 0.30,
    "gAnchorGain": 4.0,
    "gSnapDist": 0.50,
    "gTearDownDist": 2.00,
    "gMaxBoneDrift": 2.00,

    "gMotorFreq": 6.0,
    "gMotorDamp": 1.50,
    "gTorqueSpine": 180.0,
    "gTorqueLimb": 105.0,
    "gTorqueNeck": 45.0,

    "gGravComp": 0.92,
    "gFootLength": 0.24,
    "gFootBalanceAmt": 0.45,
    "gMaxAngle": 30.0,
    "gSpinThreshold": 0.50,
    "gStepPredictFwd": 0.42,
    "gStepPredictBack": 0.28,
    "gMaxStepLength": 0.70,
    "gStepHeight": 0.16,
    "gBraceTime": 0.45,
    "gGiveUpTime": 1.25,
    "gWindmillAmount": 0.25,
    "gLocoDamp": 1.25,

    # Known-good ground configuration.
    "gGroundSamples": 15,
    "gGroundExtent": 4.50,
    "gRebuildDist": 0.60,
}

# Recovery-state candidate from the verified v3.10 recovery block.
# At file offset / virtual address 0x7510C the original instruction is:
#     strb.w r6, [r8, #5]
# We change it to:
#     strh.w r6, [r8, #4]
#
# r6 is zero at this point in the recovery path, so both adjacent
# state bytes (+4 and +5) are cleared together.
RECOVERY_VA = 0x0007510C
RECOVERY_OFFSET = 0x0007510C
RECOVERY_OLD = bytes.fromhex("88 f8 05 60")
RECOVERY_NEW = bytes.fromhex("a8 f8 04 60")

def file_offset(address):
    return DATA_OFFSET + (address - DATA_VADDR)

def read_float(data, off):
    return struct.unpack_from("<f", data, off)[0]

def write_float(data, off, value):
    struct.pack_into("<f", data, off, float(value))

def main():
    if not INPUT.exists():
        print("ERROR: libBuggyRagdoll.so not found.")
        sys.exit(1)

    data = bytearray(INPUT.read_bytes())

    print("Buggy Ragdoll v3.10 - ALL-IN-ONE TEST PATCH")
    print("============================================")
    print()

    # Verify the recovery patch target before touching anything.
    if RECOVERY_OFFSET + 4 > len(data):
        print("ERROR: recovery patch offset is outside the library.")
        sys.exit(2)

    current = bytes(data[RECOVERY_OFFSET:RECOVERY_OFFSET + 4])
    print(f"Recovery @ 0x{RECOVERY_VA:08X}: {current.hex(' ')}")

    if current != RECOVERY_OLD:
        print(f"Expected: {RECOVERY_OLD.hex(' ')}")
        print("ERROR: library does not match the expected v3.10 recovery block.")
        print("No output was written.")
        sys.exit(3)

    print()
    print("Applying configuration:")
    print("-----------------------")

    for name, value in CONFIG.items():
        address = GLOBALS[name]
        off = file_offset(address)

        if off < 0 or off + 4 > len(data):
            print(f"ERROR: invalid data offset for {name}")
            sys.exit(4)

        if name == "gGroundSamples":
            old = struct.unpack_from("<I", data, off)[0]
            struct.pack_into("<I", data, off, int(value))
            print(f"{name:22} {old} -> {int(value)}")
        else:
            old = read_float(data, off)
            write_float(data, off, value)
            print(f"{name:22} {old:.3f} -> {float(value):.3f}")

    print()
    print("Applying recovery-state synchronization:")
    print("-----------------------------------------")
    data[RECOVERY_OFFSET:RECOVERY_OFFSET + 4] = RECOVERY_NEW
    print(f"0x{RECOVERY_VA:08X}: {RECOVERY_OLD.hex(' ')} -> {RECOVERY_NEW.hex(' ')}")

    OUTPUT.write_bytes(data)

    print()
    print("SUCCESS")
    print(f"Created: {OUTPUT}")
    print("Original library was NOT modified.")
    print()
    print("This is an experimental combined test build.")
    print("If recovery still fails, the remaining problem is the GTA")
    print("animation-task handoff, which cannot safely be fixed by")
    print("changing these configuration values alone.")

if __name__ == "__main__":
    main()
