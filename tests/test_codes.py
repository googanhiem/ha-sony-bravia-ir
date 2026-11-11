"""Tests for the Sony SIRC encoding and decoding."""

from infrared_protocols.commands.sony import SonyCommand
import pytest

from custom_components.sony_bravia_ir.codes import (
    SIRC_FRAMES_PER_COMMAND,
    SircFrame,
    SonyBraviaCode,
    decode_sirc,
)


def test_power_off_timings() -> None:
    """Test the 12-bit power off frame matches the SIRC spec."""
    timings = SonyBraviaCode.POWER_OFF.to_command().get_raw_timings()
    frame_len = len(timings) // SIRC_FRAMES_PER_COMMAND
    frame = timings[:frame_len]
    # Leader + 12 bits (space, mark) + trailer
    assert frame_len == 1 + 12 * 2 + 1
    assert frame[0] == 2400
    # Command 0x2F (LSB first): 1,1,1,1,0,1,0 then address 1: 1,0,0,0,0
    marks = frame[2:-1:2]
    assert [1 if mark == 1200 else 0 for mark in marks] == [
        1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0
    ]  # fmt: skip
    # Each frame lasts exactly 45 ms.
    assert sum(abs(value) for value in frame) == 45000
    assert timings == frame * SIRC_FRAMES_PER_COMMAND


def test_commands_match_library_encoder() -> None:
    """Test each frame is identical to the infrared-protocols encoder."""
    for code in SonyBraviaCode:
        address, address_bits, command = code.value
        single = SonyCommand(
            address=address, address_bits=address_bits, command=command
        ).get_raw_timings()
        assert code.to_command().get_raw_timings() == single * 3, code


@pytest.mark.parametrize("code", list(SonyBraviaCode))
def test_round_trip(code: SonyBraviaCode) -> None:
    """Test every code decodes back to itself."""
    frame = decode_sirc(code.to_command().get_raw_timings())
    assert frame == code.frame
    assert SonyBraviaCode.from_frame(frame) is code


def test_decode_unsigned_and_jittered() -> None:
    """Test decoding tolerates unsigned timings and receiver jitter."""
    timings = SonyBraviaCode.HDMI_2.to_command().get_raw_timings()
    jittered = [
        abs(value) + (90 if idx % 3 else -90) for idx, value in enumerate(timings)
    ]
    assert decode_sirc(jittered) == SircFrame(0x1A, 8, 0x5B)


def test_decode_frame_without_trailer() -> None:
    """Test decoding a single frame cut off right after the last bit."""
    timings = SonyBraviaCode.VOLUME_UP.to_command().get_raw_timings()
    assert decode_sirc(timings[: 1 + 12 * 2]) == SircFrame(0x01, 5, 0x12)


@pytest.mark.parametrize(
    "timings",
    [
        [],
        [1, 2, 3, 4],
        # NEC leader
        [9000, -4500, 560, -560, 560],
        # Leader followed by too few bits
        [2400, -600, 600, -600, 1200, -20000],
    ],
)
def test_decode_invalid(timings: list[int]) -> None:
    """Test non-SIRC signals are rejected."""
    assert decode_sirc(timings) is None


def test_decode_20_bit() -> None:
    """Test 20-bit SIRC frames are decoded."""
    timings = SonyCommand(address=0x1A93, address_bits=13, command=21).get_raw_timings()
    assert decode_sirc(timings) == SircFrame(0x1A93, 13, 21)
