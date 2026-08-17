import struct
import sys
from pathlib import Path


INPUT = Path("libBuggyRagdoll.so")
OUTPUT = Path("libBuggyRagdoll_fixed2.so")

DATA_VADDR = 0x00193BA8
DATA_OFFSET = 0x00191BA8


GLOBALS = {
    "gMaxRagdollTime": 0x00193BC4,
    "gBlendTime":      0x00193BBC,
    "gRecoverTime":    0x00193BC0,

    "gGravity":        0x00193BCC,
    "gTeleportVel":   0x00193BD0,
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


# Recovery-oriented preset.
#
# Ground-related values are retained from the successful
# first patch.
#
# The important changes are:
#
# - shorter ragdoll lifetime
# - longer but smoother blend
# - stronger recovery damping
# - lower motor frequency
# - less aggressive anchor correction
# - tighter bone-drift tolerance
#
# This is intended to encourage the existing recovery code
# to reach the animation state instead of leaving the ped
# permanently simulated.


PATCH = {
    "gMaxRagdollTime": 3.50,
    "gBlendTime":      0.20,
    "gRecoverTime":    0.90,

    "gGravity":       -9.81,
    "gTeleportVel":   25.0,
    "gImpactDeltaV":   8.5,
    "gFallSpeed":      2.0,

    "gAnchorBlend":    0.30,
    "gAnchorGain":     4.0,
    "gSnapDist":       0.50,
    "gTearDownDist":   2.0,
    "gMaxBoneDrift":   2.00,

    "gMotorFreq":       6.0,
    "gMotorDamp":       1.50,

    "gTorqueSpine":   180.0,
    "gTorqueLimb":    105.0,
    "gTorqueNeck":     45.0,

    "gGravComp":        0.92,
    "gFootLength":      0.24,
    "gFootBalanceAmt":  0.45,

    "gMaxAngle":       30.0,
    "gSpinThreshold":   0.50,

    "gStepPredictFwd":  0.42,
    "gStepPredictBack":0.28,
    "gMaxStepLength":   0.70,
    "gStepHeight":      0.16,

    "gBraceTime":       0.45,
    "gGiveUpTime":      1.25,

    "gWindmillAmount":  0.25,
    "gLocoDamp":       1.25,

    # Keep the successful ground fix.
    "gGroundSamples":  15,
    "gGroundExtent":    4.5,

    "gRebuildDist":     0.60,
}


def file_offset(address):
    return DATA_OFFSET + (address - DATA_VADDR)


def read_float(data, offset):
    return struct.unpack_from("<f", data, offset)[0]


def write_float(data, offset, value):
    struct.pack_into("<f", data, offset, float(value))


def main():

    if not INPUT.exists():
        print("ERROR: libBuggyRagdoll.so not found.")
        print("Upload the ORIGINAL v3.10 library to the repository root.")
        sys.exit(1)

    data = bytearray(INPUT.read_bytes())

    print("==============================================")
    print(" Buggy Ragdoll v3.10 - Recovery Fix")
    print("==============================================")
    print()

    print("Original configuration:")
    print("----------------------")

    for name, address in GLOBALS.items():

        offset = file_offset(address)

        if offset < 0 or offset + 4 > len(data):
            print(f"ERROR: invalid offset for {name}")
            sys.exit(1)

        if name == "gGroundSamples":
            value = struct.unpack_from("<I", data, offset)[0]
            print(f"{name:22} {value}")
        else:
            value = read_float(data, offset)
            print(f"{name:22} {value:.4f}")

    print()
    print("Applying recovery-oriented configuration...")
    print("---------------------------------------------")

    for name, value in PATCH.items():

        address = GLOBALS[name]
        offset = file_offset(address)

        if name == "gGroundSamples":
            struct.pack_into("<I", data, offset, int(value))
            print(f"{name:22} -> {int(value)}")
        else:
            write_float(data, offset, value)
            print(f"{name:22} -> {value}")

    OUTPUT.write_bytes(data)

    print()
    print("SUCCESS")
    print()
    print(f"Created: {OUTPUT}")
    print()
    print("Original library was NOT modified.")


if __name__ == "__main__":
    main()
