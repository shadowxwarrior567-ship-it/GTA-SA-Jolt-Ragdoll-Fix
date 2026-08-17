import struct
import sys
from pathlib import Path


INPUT = Path("libBuggyRagdoll.so")
OUTPUT = Path("libBuggyRagdoll_fixed.so")


# Exact .data layout of Buggy Ragdoll v3.10
#
# .data virtual address:
#     0x00193BA8
#
# .data file offset:
#     0x00191BA8
#
# Therefore:
#
# file_offset = 0x191BA8 + (global_address - 0x193BA8)


DATA_VADDR = 0x00193BA8
DATA_OFFSET = 0x00191BA8


GLOBALS = {
    "gMaxRagdollTime": 0x00193BC4,
    "gBlendTime":      0x00193BBC,
    "gRecoverTime":    0x00193BC0,

    "gGravity":        0x00193BCC,
    "gTeleportVel":   0x00193BD0,
    "gImpactDeltaV":   0x00193BD4,
    "gFallSpeed":     0x00193BD8,

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


# ------------------------------------------------------------
# Integrated stability preset
#
# These values are intentionally conservative.
#
# The goal is:
# - reduce excessive bone drift
# - reduce violent motor corrections
# - make ground stabilization less aggressive
# - improve recovery
# - keep the existing Jolt system intact
# ------------------------------------------------------------

PATCH = {
    "gMaxRagdollTime": 5.0,
    "gBlendTime":      0.08,
    "gRecoverTime":    1.50,

    "gGravity":       -9.81,
    "gTeleportVel":   25.0,
    "gImpactDeltaV":   8.5,
    "gFallSpeed":      2.0,

    "gAnchorBlend":    0.45,
    "gAnchorGain":     5.0,
    "gSnapDist":       0.65,
    "gTearDownDist":   2.5,
    "gMaxBoneDrift":   2.75,

    "gMotorFreq":      10.0,
    "gMotorDamp":       1.15,

    "gTorqueSpine":   220.0,
    "gTorqueLimb":    135.0,
    "gTorqueNeck":     50.0,

    "gGravComp":        0.92,
    "gFootLength":      0.24,
    "gFootBalanceAmt":  0.45,

    "gMaxAngle":       30.0,
    "gSpinThreshold":   0.50,

    "gStepPredictFwd":  0.42,
    "gStepPredictBack":0.28,
    "gMaxStepLength":   0.70,
    "gStepHeight":      0.16,

    "gBraceTime":       0.60,
    "gGiveUpTime":      2.0,

    "gWindmillAmount":  0.35,
    "gLocoDamp":       1.10,

    "gGroundSamples":  15,
    "gGroundExtent":    4.5,

    "gRebuildDist":     0.75,
}


def file_offset(address):
    return DATA_OFFSET + (address - DATA_VADDR)


def read_float(data, offset):
    return struct.unpack_from("<f", data, offset)[0]


def write_float(data, offset, value):
    struct.pack_into("<f", data, offset, float(value))


def main():
    if not INPUT.exists():
        print("ERROR: libBuggyRagdoll.so was not found.")
        print("Put the original Buggy Ragdoll v3.10 library in the repository root.")
        sys.exit(1)

    data = bytearray(INPUT.read_bytes())

    print("Buggy Ragdoll v3.10 integrated stability patch")
    print("")

    print("Original values:")
    print("----------------")

    for name, address in GLOBALS.items():
        offset = file_offset(address)

        if name == "gGroundSamples":
            value = struct.unpack_from("<I", data, offset)[0]
            print(f"{name:20} {value}")
        else:
            value = read_float(data, offset)
            print(f"{name:20} {value:.4f}")

    print("")
    print("Applying stability preset...")
    print("-----------------------------")

    for name, value in PATCH.items():
        address = GLOBALS[name]
        offset = file_offset(address)

        if name == "gGroundSamples":
            struct.pack_into("<I", data, offset, int(value))
            print(f"{name:20} -> {int(value)}")
        else:
            write_float(data, offset, value)
            print(f"{name:20} -> {value}")

    OUTPUT.write_bytes(data)

    print("")
    print("SUCCESS")
    print(f"Created: {OUTPUT}")
    print("")
    print("The original library was not modified.")


if __name__ == "__main__":
    main()
