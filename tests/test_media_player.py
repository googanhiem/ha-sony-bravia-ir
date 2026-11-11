"""Tests for the Sony Bravia IR media player."""

from typing import Any

import pytest

from custom_components.sony_bravia_ir.codes import SonyBraviaCode
from homeassistant.components.media_player import (
    ATTR_INPUT_SOURCE,
    ATTR_INPUT_SOURCE_LIST,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_MEDIA_NEXT_TRACK,
    SERVICE_MEDIA_PAUSE,
    SERVICE_MEDIA_PLAY,
    SERVICE_MEDIA_PREVIOUS_TRACK,
    SERVICE_MEDIA_STOP,
    SERVICE_SELECT_SOURCE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
    SERVICE_VOLUME_UP,
)
from homeassistant.const import (
    ATTR_ASSUMED_STATE,
    ATTR_ENTITY_ID,
    STATE_OFF,
    STATE_ON,
    STATE_UNAVAILABLE,
    Platform,
)
from homeassistant.core import HomeAssistant, State
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .common import MockConfigEntry, mock_restore_cache
from .conftest import EMITTER_ENTITY_ID, MockInfraredEmitterEntity

ENTITY_ID = "media_player.sony_bravia_tv"


@pytest.fixture
def platforms() -> list[Platform]:
    """Return the platforms to set up."""
    return [Platform.MEDIA_PLAYER]


@pytest.mark.usefixtures("init_integration")
async def test_entity(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    device_registry: dr.DeviceRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the media player and its device."""
    state = hass.states.get(ENTITY_ID)
    assert state is not None
    assert state.state == STATE_ON
    assert state.attributes[ATTR_ASSUMED_STATE] is True
    assert state.attributes[ATTR_INPUT_SOURCE_LIST] == [
        "TV",
        "HDMI 1",
        "HDMI 2",
        "HDMI 3",
        "HDMI 4",
    ]
    entity_entry = entity_registry.async_get(ENTITY_ID)
    assert entity_entry.unique_id == f"{mock_config_entry.entry_id}_media_player"
    device = device_registry.async_get(entity_entry.device_id)
    assert device.manufacturer == "Sony"
    assert device.model == "KDL-42W653A"


@pytest.mark.parametrize(
    ("service", "service_data", "expected_code"),
    [
        (SERVICE_TURN_ON, {}, SonyBraviaCode.POWER_ON),
        (SERVICE_TURN_OFF, {}, SonyBraviaCode.POWER_OFF),
        (SERVICE_VOLUME_UP, {}, SonyBraviaCode.VOLUME_UP),
        (SERVICE_VOLUME_DOWN, {}, SonyBraviaCode.VOLUME_DOWN),
        (SERVICE_VOLUME_MUTE, {"is_volume_muted": True}, SonyBraviaCode.MUTE),
        (SERVICE_MEDIA_NEXT_TRACK, {}, SonyBraviaCode.CHANNEL_UP),
        (SERVICE_MEDIA_PREVIOUS_TRACK, {}, SonyBraviaCode.CHANNEL_DOWN),
        (SERVICE_MEDIA_PLAY, {}, SonyBraviaCode.PLAY),
        (SERVICE_MEDIA_PAUSE, {}, SonyBraviaCode.PAUSE),
        (SERVICE_MEDIA_STOP, {}, SonyBraviaCode.STOP),
        (SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "TV"}, SonyBraviaCode.TV),
        (SERVICE_SELECT_SOURCE, {ATTR_INPUT_SOURCE: "HDMI 3"}, SonyBraviaCode.HDMI_3),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_action_sends_code(
    hass: HomeAssistant,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
    service: str,
    service_data: dict[str, Any],
    expected_code: SonyBraviaCode,
) -> None:
    """Test each media player action sends the right IR code."""
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        service,
        {ATTR_ENTITY_ID: ENTITY_ID, **service_data},
        blocking=True,
    )
    assert mock_infrared_emitter_entity.send_command_calls == [expected_code]


@pytest.mark.usefixtures("init_integration")
async def test_assumed_state_tracking(hass: HomeAssistant) -> None:
    """Test power and source are tracked optimistically."""
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_TURN_OFF,
        {ATTR_ENTITY_ID: ENTITY_ID},
        blocking=True,
    )
    assert hass.states.get(ENTITY_ID).state == STATE_OFF

    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: ENTITY_ID}, blocking=True
    )
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        SERVICE_SELECT_SOURCE,
        {ATTR_ENTITY_ID: ENTITY_ID, ATTR_INPUT_SOURCE: "HDMI 2"},
        blocking=True,
    )
    state = hass.states.get(ENTITY_ID)
    assert state.state == STATE_ON
    assert state.attributes[ATTR_INPUT_SOURCE] == "HDMI 2"


@pytest.mark.usefixtures("init_integration")
async def test_invalid_source(
    hass: HomeAssistant, mock_infrared_emitter_entity: MockInfraredEmitterEntity
) -> None:
    """Test selecting an unknown source raises."""
    with pytest.raises(ServiceValidationError):
        await hass.services.async_call(
            MEDIA_PLAYER_DOMAIN,
            SERVICE_SELECT_SOURCE,
            {ATTR_ENTITY_ID: ENTITY_ID, ATTR_INPUT_SOURCE: "SCART"},
            blocking=True,
        )
    assert mock_infrared_emitter_entity.send_command_calls == []


@pytest.mark.usefixtures(
    "mock_infrared_emitter_entity",
    "mock_infrared_receiver_entity",
    "mock_code_to_command",
)
@pytest.mark.parametrize(
    ("restored", "expected_state", "expected_source"),
    [
        (State(ENTITY_ID, STATE_OFF), STATE_OFF, None),
        (State(ENTITY_ID, STATE_ON, {ATTR_INPUT_SOURCE: "HDMI 4"}), STATE_ON, "HDMI 4"),
        (State(ENTITY_ID, STATE_ON, {ATTR_INPUT_SOURCE: "SCART"}), STATE_ON, None),
    ],
)
async def test_restore_state(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    restored: State,
    expected_state: str,
    expected_source: str | None,
) -> None:
    """Test the assumed state is restored after a restart."""
    mock_restore_cache(hass, [restored])
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get(ENTITY_ID)
    assert state.state == expected_state
    assert state.attributes.get(ATTR_INPUT_SOURCE) == expected_source


@pytest.mark.usefixtures("init_integration")
async def test_availability_follows_emitter(hass: HomeAssistant) -> None:
    """Test the media player follows the emitter availability."""
    hass.states.async_set(EMITTER_ENTITY_ID, STATE_UNAVAILABLE)
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_UNAVAILABLE

    hass.states.async_set(EMITTER_ENTITY_ID, "2026-01-01T00:00:00.000+00:00")
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY_ID).state == STATE_ON


@pytest.mark.parametrize(
    "mock_config_entry",
    [
        MockConfigEntry(
            domain="sony_bravia_ir",
            data={"infrared_receiver_entity_id": "infrared.test_ir_receiver"},
        )
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_no_emitter_no_media_player(hass: HomeAssistant) -> None:
    """Test no media player is created without an emitter."""
    assert hass.states.get(ENTITY_ID) is None
