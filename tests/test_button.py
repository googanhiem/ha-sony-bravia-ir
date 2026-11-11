"""Tests for the Sony Bravia IR buttons."""

import pytest

from custom_components.sony_bravia_ir.button import BUTTON_DESCRIPTIONS
from custom_components.sony_bravia_ir.codes import SonyBraviaCode
from custom_components.sony_bravia_ir.const import BraviaGeneration
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID, STATE_UNAVAILABLE, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .common import MockConfigEntry
from .conftest import EMITTER_ENTITY_ID, MockInfraredEmitterEntity


@pytest.fixture
def platforms() -> list[Platform]:
    """Return the platforms to set up."""
    return [Platform.BUTTON]


@pytest.mark.parametrize(
    ("generation", "expected_disabled"),
    [
        (
            BraviaGeneration.ANDROID,
            {"sen", "teletext", "jump", "picture_off", "help", "discover"},
        ),
        (
            BraviaGeneration.CLASSIC,
            {
                "netflix",
                "youtube",
                "google_play",
                "action_menu",
                "picture_off",
                "help",
                "discover",
            },
        ),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_entities_created(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
    expected_disabled: set[str],
) -> None:
    """Test all buttons are registered, with keys missing on the remote disabled."""
    entries = er.async_entries_for_config_entry(
        entity_registry, mock_config_entry.entry_id
    )
    assert len(entries) == len(BUTTON_DESCRIPTIONS)
    disabled = {entry.entity_id for entry in entries if entry.disabled_by}
    assert disabled == {f"button.sony_bravia_tv_{key}" for key in expected_disabled}


@pytest.mark.parametrize(
    ("entity_id", "expected_code"),
    [
        ("button.sony_bravia_tv_power", SonyBraviaCode.POWER),
        ("button.sony_bravia_tv_hdmi_1", SonyBraviaCode.HDMI_1),
        ("button.sony_bravia_tv_back", SonyBraviaCode.RETURN),
        ("button.sony_bravia_tv_ok", SonyBraviaCode.OK),
        ("button.sony_bravia_tv_7", SonyBraviaCode.NUM_7),
        ("button.sony_bravia_tv_red", SonyBraviaCode.RED),
        ("button.sony_bravia_tv_guide", SonyBraviaCode.GUIDE),
        ("button.sony_bravia_tv_youtube", SonyBraviaCode.YOUTUBE),
        ("button.sony_bravia_tv_netflix", SonyBraviaCode.NETFLIX),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_press_sends_code(
    hass: HomeAssistant,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
    entity_id: str,
    expected_code: SonyBraviaCode,
) -> None:
    """Test pressing a button sends its IR code."""
    await hass.services.async_call(
        BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    assert mock_infrared_emitter_entity.send_command_calls == [expected_code]


@pytest.mark.usefixtures("init_integration")
async def test_availability_follows_emitter(hass: HomeAssistant) -> None:
    """Test buttons follow the emitter availability."""
    hass.states.async_set(EMITTER_ENTITY_ID, STATE_UNAVAILABLE)
    await hass.async_block_till_done()
    assert hass.states.get("button.sony_bravia_tv_power").state == STATE_UNAVAILABLE
