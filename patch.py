#!/usr/bin/env python3
from pathlib import Path
import struct
import sys

INPUT = Path("libBuggyRagdoll.so")
OUTPUT = Path("libBuggyRagdoll_mega_test.so")

DATA_VADDR = 0x00193BA8
DATA_OFFSET = 0x00191BA8

GLOBALS = {
    "gMaxRagdollTime": 0x00193BC4,
    "gBlendTime": 0x00193BBC,
    "gRecoverTime": 0x00193BC0,
    "gGravity": 0x00193BCC,
    "gTeleportVel": 0x00193BD0,
    "gImpactDeltaV": 0x00193BD4,
    "gFallSpeed": 0x00193BD8,
    "gAnchorBlend": 0x00193BE4,
    "gAnchorGain": 0x00193BE8,
    "gSnapDist": 0x00193BEC,
    "gTearDownDist": 0x00193BF0,
    "gMaxBoneDrift": 0x00193BF4,
    "gMotorFreq": 0x00193BF8,
    "gMotorDamp": 0x00193BFC,
    "gTorqueSpine": 0x00193C00,
    "gTorqueLimb": 0x00193C04,
    "gTorqueNeck": 0x00193C08,
    "gGravComp": 0x00193C0C,
    "gFootLength": 0x00193C10,
    "gFootBalanceAmt": 0x00193C14,
    "gMaxAngle": 0x00193C18,
    "gSpinThreshold": 0x00193C1C,
    "gStepPredictFwd": 0x00193C20,
    "gStepPredictBack": 0x00193C24,
    "gMaxStepLength": 0x00193C28,
    "gStepHeight": 0x00193C2C,
    "gBraceTime": 0x00193C30,
    "gGiveUpTime": 0x00193C34,
    "gWindmillAmount": 0x00193C38,
    "gLocoDamp": 0x00193C3C,
    "gGroundSamples": 0x00193C40,
    "gGroundExtent": 0x00193C44,
    "gRebuildDist": 0x00193C48,
}

CONFIG = {
    "gMaxRagdollTime": 4.5,
    "gBlendTime": 0.30,
    "gRecoverTime": 1.50,
    "gGravity": -9.81,
    "gTeleportVel": 25.0,
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
    "gGroundSamples": 15,
    "gGroundExtent": 4.50,
    "gRebuildDist": 0.60,
}

# Known v3.10 damage hook test patch.
DAMAGE_OFFSET = 0x723D6
DAMAGE_OLD = bytes.fromhex("09 d0")
DAMAGE_NEW = bytes.fromhex("0a e0")

# Known v3.10 recovery-state test patch.
RECOVERY_OFFSET = 0x7510C
RECOVERY_OLD = bytes.fromhex("88 f8 05 60")
RECOVERY_NEW = bytes.fromhex("a8 f8 04 60")

def foff(va):
    return DATA_OFFSET + (va - DATA_VADDR)

def main():
    if not INPUT.exists():
        print("ERROR: libBuggyRagdoll.so not found.")
        sys.exit(1)

    data = bytearray(INPUT.read_bytes())

    print("Buggy Ragdoll v3.10 — MEGA TEST PATCH")
    print("--------------------------------------")

    damage = bytes(data[DAMAGE_OFFSET:DAMAGE_OFFSET+2])
    recovery = bytes(data[RECOVERY_OFFSET:RECOVERY_OFFSET+4])

    if damage != DAMAGE_OLD:
        print("ERROR: damage hook does not match expected original v3.10 bytes.")
        print("Found:", damage.hex(" "))
        print("Expected:", DAMAGE_OLD.hex(" "))
        sys.exit(2)

    if recovery != RECOVERY_OLD:
        print("ERROR: recovery block does not match expected original v3.10 bytes.")
        print("Found:", recovery.hex(" "))
        print("Expected:", RECOVERY_OLD.hex(" "))
        sys.exit(3)

    print("Applying ragdoll configuration...")
    for name, value in CONFIG.items():
        off = foff(GLOBALS[name])
        if off < 0 or off + 4 > len(data):
            print("ERROR: invalid data offset:", name)
            sys.exit(4)

        if name == "gGroundSamples":
            struct.pack_into("<I", data, off, int(value))
        else:
            struct.pack_into("<f", data, off, float(value))

    print("Applying gunshot/damage ragdoll filter...")
    data[DAMAGE_OFFSET:DAMAGE_OFFSET+2] = DAMAGE_NEW

    print("Applying recovery-state synchronization...")
    data[RECOVERY_OFFSET:RECOVERY_OFFSET+4] = RECOVERY_NEW

    OUTPUT.write_bytes(data)

    print()
    print("SUCCESS:", OUTPUT)
    print()
    print("NOTE:")
    print("The save/load location problem is NOT blindly patched here.")
    print("The supplied symbol/disassembly data identifies PedProcessControl")
    print("as relevant, but does not safely identify the exact position-write")
    print("instruction. Patching the whole hook could break the game.")
    print("This build therefore combines every VERIFIED patch without making")
    print("an unsafe save-system modification.")

if __name__ == "__main__":
    main()
