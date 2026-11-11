"""Sony SIRC IR codes for the Sony Bravia KDL-42W653A.

Sony Bravia sets from the 2013 generation (W6xxA, W8xxA, ...) mix three
flavours of the Sony SIRC protocol:

- 12-bit SIRC on address 1 (5 address bits) for the classic TV keys.
- 15-bit SIRC on addresses 0x1A, 0x97 and 0xA4 (8 address bits) for the
  keys added later (discrete HDMI inputs, transport keys, colour keys, ...).

The codes below match the IRCC table these sets report over their network
API, which encodes exactly the SIRC address/command pairs of the bundled
RM-ED0xx remote.

Sony receivers only accept a command after seeing the same frame several
times, so every command is sent as three consecutive frames, just like a
short press on the original remote.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from typing import override

from infrared_protocols.commands import Command
from infrared_protocols.commands.sony import SonyCommand

SIRC_FRAMES_PER_COMMAND = 3

_ADDR_TV = (0x01, 5)
_ADDR_INPUT = (0x1A, 8)
_ADDR_EXT = (0x97, 8)
_ADDR_GUIDE = (0xA4, 8)


@dataclass(frozen=True, slots=True)
class SircFrame:
    """A decoded Sony SIRC frame."""

    address: int
    address_bits: int
    command: int


class SonyRepeatedCommand(SonyCommand):
    """A Sony SIRC command sent as several identical frames.

    Older infrared-protocols releases have no repeat support on SonyCommand,
    so the repetition is done here to work on every supported HA version.
    """

    def __init__(
        self,
        *,
        address: int,
        address_bits: int,
        command: int,
        frames: int = SIRC_FRAMES_PER_COMMAND,
    ) -> None:
        """Initialize the command."""
        super().__init__(address=address, address_bits=address_bits, command=command)
        self.frames = frames

    @override
    def get_raw_timings(self) -> list[int]:
        """Return the raw timings of all frames."""
        return super().get_raw_timings() * self.frames


@unique
class SonyBraviaCode(Enum):
    """IR codes of the Sony KDL-42W653A as (address, address_bits, command)."""

    # Power
    POWER = (*_ADDR_TV, 0x15)
    POWER_ON = (*_ADDR_TV, 0x2E)
    POWER_OFF = (*_ADDR_TV, 0x2F)

    # Volume / channel
    VOLUME_UP = (*_ADDR_TV, 0x12)
    VOLUME_DOWN = (*_ADDR_TV, 0x13)
    MUTE = (*_ADDR_TV, 0x14)
    CHANNEL_UP = (*_ADDR_TV, 0x10)
    CHANNEL_DOWN = (*_ADDR_TV, 0x11)

    # Inputs
    INPUT = (*_ADDR_TV, 0x25)
    TV = (*_ADDR_TV, 0x24)
    HDMI_1 = (*_ADDR_INPUT, 0x5A)
    HDMI_2 = (*_ADDR_INPUT, 0x5B)
    HDMI_3 = (*_ADDR_INPUT, 0x5C)
    HDMI_4 = (*_ADDR_INPUT, 0x5D)

    # Digits
    NUM_1 = (*_ADDR_TV, 0x00)
    NUM_2 = (*_ADDR_TV, 0x01)
    NUM_3 = (*_ADDR_TV, 0x02)
    NUM_4 = (*_ADDR_TV, 0x03)
    NUM_5 = (*_ADDR_TV, 0x04)
    NUM_6 = (*_ADDR_TV, 0x05)
    NUM_7 = (*_ADDR_TV, 0x06)
    NUM_8 = (*_ADDR_TV, 0x07)
    NUM_9 = (*_ADDR_TV, 0x08)
    NUM_0 = (*_ADDR_TV, 0x09)

    # Navigation
    NAV_UP = (*_ADDR_TV, 0x74)
    NAV_DOWN = (*_ADDR_TV, 0x75)
    NAV_LEFT = (*_ADDR_TV, 0x34)
    NAV_RIGHT = (*_ADDR_TV, 0x33)
    OK = (*_ADDR_TV, 0x65)
    HOME = (*_ADDR_TV, 0x60)
    RETURN = (*_ADDR_EXT, 0x23)
    OPTIONS = (*_ADDR_EXT, 0x36)
    EXIT = (*_ADDR_TV, 0x63)
    DISPLAY = (*_ADDR_TV, 0x3A)
    GUIDE = (*_ADDR_GUIDE, 0x5B)
    SYNC_MENU = (*_ADDR_INPUT, 0x58)
    SEN = (*_ADDR_INPUT, 0x7D)
    NETFLIX = (*_ADDR_INPUT, 0x7C)

    # Colour keys
    RED = (*_ADDR_EXT, 0x25)
    GREEN = (*_ADDR_EXT, 0x26)
    YELLOW = (*_ADDR_EXT, 0x27)
    BLUE = (*_ADDR_EXT, 0x24)

    # Picture / sound
    PICTURE_MODE = (*_ADDR_TV, 0x64)
    PICTURE_OFF = (*_ADDR_TV, 0x3E)
    WIDE = (*_ADDR_GUIDE, 0x3D)
    AUDIO = (*_ADDR_TV, 0x17)
    SUBTITLE = (*_ADDR_EXT, 0x28)
    TELETEXT = (*_ADDR_TV, 0x3F)
    JUMP = (*_ADDR_TV, 0x3B)

    # Transport (USB / DLNA playback)
    PLAY = (*_ADDR_EXT, 0x1A)
    PAUSE = (*_ADDR_EXT, 0x19)
    STOP = (*_ADDR_EXT, 0x18)
    REWIND = (*_ADDR_EXT, 0x1B)
    FAST_FORWARD = (*_ADDR_EXT, 0x1C)
    PREVIOUS = (*_ADDR_EXT, 0x3C)
    NEXT = (*_ADDR_EXT, 0x3D)

    @property
    def frame(self) -> SircFrame:
        """Return the SIRC frame of this code."""
        address, address_bits, command = self.value
        return SircFrame(address, address_bits, command)

    def to_command(self) -> Command:
        """Build the IR command for this code."""
        address, address_bits, command = self.value
        return SonyRepeatedCommand(
            address=address, address_bits=address_bits, command=command
        )

    @classmethod
    def from_frame(cls, frame: SircFrame) -> SonyBraviaCode | None:
        """Return the code matching a decoded frame, if any."""
        return _FRAME_TO_CODE.get(frame)


_FRAME_TO_CODE: dict[SircFrame, SonyBraviaCode] = {
    code.frame: code for code in SonyBraviaCode
}

TV_ADDRESSES: frozenset[tuple[int, int]] = frozenset(
    {_ADDR_TV, _ADDR_INPUT, _ADDR_EXT, _ADDR_GUIDE}
)

# SIRC decoding tolerances, in microseconds.
_LEADER_MIN, _LEADER_MAX = 1800, 3000
_SPACE_MIN, _SPACE_MAX = 300, 1000
_ZERO_MIN, _ZERO_MAX = 300, 900
_ONE_MIN, _ONE_MAX = 900, 1600
_VALID_BIT_COUNTS = (12, 15, 20)


def decode_sirc(timings: list[int]) -> SircFrame | None:
    """Decode the first valid Sony SIRC frame found in raw timings.

    Accepts signed (mark positive, space negative) or unsigned timings.
    """
    values = [abs(value) for value in timings]
    length = len(values)
    for start in range(length):
        if not _LEADER_MIN <= values[start] <= _LEADER_MAX:
            continue
        bits: list[int] = []
        pos = start + 1
        while (
            len(bits) < 20
            and pos + 1 < length
            and _SPACE_MIN <= values[pos] <= _SPACE_MAX
        ):
            mark = values[pos + 1]
            if _ZERO_MIN <= mark < _ZERO_MAX:
                bits.append(0)
            elif _ONE_MIN <= mark <= _ONE_MAX:
                bits.append(1)
            else:
                break
            pos += 2
        if len(bits) not in _VALID_BIT_COUNTS:
            continue
        # The frame must be followed by a gap (or end of capture), otherwise
        # this is a longer frame that failed to decode.
        if pos < length and values[pos] <= _SPACE_MAX:
            continue
        command = sum(bit << idx for idx, bit in enumerate(bits[:7]))
        address = sum(bit << idx for idx, bit in enumerate(bits[7:]))
        return SircFrame(address, len(bits) - 7, command)
    return None
