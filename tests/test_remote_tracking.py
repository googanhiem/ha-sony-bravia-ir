"""Tests for the media player following the physical remote."""

from datetime import timedelta

from freezegun.api import FrozenDateTimeFactory
import pytest

from custom_components.sony_bravia_ir.codes import SonyBraviaCode, SonyRepeatedCommand
from custom_components.sony_bravia_ir.const import CONF_TRACK_PHYSICAL_REMOTE
from homeassistant.components.infrared import InfraredReceivedSignal
from homeassistant.components.media_player import (
    ATTR_INPUT_SOURCE,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_SELECT_SOURCE,
    SERVICE_TURN_OFF,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON, Platform
from homeassistant.core import HomeAssistant

from .common import MockConfigEntry
from .conftest import MockInfraredReceiverEntity

ENTITY_ID = "media_player.sony_bravia_tv"


@pytest.fixture
def platforms() -> list[Platform]:
    """Return the platforms to set up."""
    return [Platform.EVENT, Platform.MEDIA_PLAYER]


def _press(
    receiver: MockInfraredReceiverEntity,
    freezer: FrozenDateTimeFactory,
    code: SonyBraviaCode,
) -> None:
    """Press a key on the remote, far enough apart to not be a repeat."""
    freezer.tick(timedelta(seconds=1))
    address, address_bits, command = code.value
    timings = SonyRepeatedCommand(
        address=address, address_bits=address_bits, command=command
    ).get_raw_timings()
    receiver._handle_received_signal(InfraredReceivedSignal(timings=timings))


@pytest.mark.parametrize(
    ("code", "expected_state"),
    [
        (SonyBraviaCode.POWER_OFF, STATE_OFF),
        (SonyBraviaCode.POWER_ON, STATE_ON),
        (SonyBraviaCode.POWER, STATE_OFF),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_remote_power_keys(
    hass: HomeAssistant,
    mock_infrared_receiver_entity: MockInfraredReceiverEntity,
    freezer: FrozenDateTimeFactory,
    code: SonyBraviaCode,
    expected_state: str,
) -> None:
    """Test the remote power keys update the assumed power state."""
    _press(mock_infrared_receiver_entity, freezer, code)
    await hass.async_block_till_done()

    assert hass.states.get(ENTITY_ID).state == expected_state


@pytest.mark.usefixtures("init_integration")
async def test_remote_power_toggle_flips(
    hass: HomeAssistant,
    mock_infrared_receiver_entity: MockInfraredReceiverEntity,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test the remote power toggle flips the assumed state each press."""
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: ENTITY_ID},
        blocking=True,
    )

    _press(mock_infrared_receiver_entity, freezer, SonyBraviaCode.POWER)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_ON

    _press(mock_infrared_receiver_entity, freezer, SonyBraviaCode.POWER)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_OFF


@pytest.mark.parametrize(
    ("code", "expected_source"),
    [
        (SonyBraviaCode.HDMI_2, "HDMI 2"),
        (SonyBraviaCode.HDMI_4, "HDMI 4"),
        (SonyBraviaCode.TV, "TV"),
        (SonyBraviaCode.INPUT, None),
        (SonyBraviaCode.VOLUME_UP, "HDMI 1"),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_remote_source_keys(
    hass: HomeAssistant,
    mock_infrared_receiver_entity: MockInfraredReceiverEntity,
    freezer: FrozenDateTimeFactory,
    code: SonyBraviaCode,
    expected_source: str | None,
) -> None:
    """Test input keys set or clear the source, and other keys leave it."""
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_SELECT_SOURCE,
        {ATTR_ENTITY_ID: ENTITY_ID, ATTR_INPUT_SOURCE: "HDMI 1"},
        blocking=True,
    )

    _press(mock_infrared_receiver_entity, freezer, code)
    await hass.async_block_till_done()

    state = hass.states.get(ENTITY_ID)
    assert state.state == STATE_ON
    assert state.attributes.get(ATTR_INPUT_SOURCE) == expected_source


async def test_remote_ignored_when_not_tracking(
    hass: HomeAssistant,
    init_integration: MockConfigEntry,
    mock_infrared_receiver_entity: MockInfraredReceiverEntity,
    freezer: FrozenDateTimeFactory,
) -> None:
    """Test the media player ignores the remote with tracking turned off."""
    hass.config_entries.async_update_entry(
        init_integration, options={CONF_TRACK_PHYSICAL_REMOTE: False}
    )
    await hass.config_entries.async_reload(init_integration.entry_id)
    await hass.async_block_till_done()

    _press(mock_infrared_receiver_entity, freezer, SonyBraviaCode.POWER_OFF)
    await hass.async_block_till_done()

    assert hass.states.get(ENTITY_ID).state == STATE_ON
    assert (
        hass.states.get("event.sony_bravia_tv_received_command").attributes[
            "event_type"
        ]
        == "power_off"
    )
