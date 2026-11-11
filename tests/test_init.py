"""Tests for the Sony Bravia IR setup and diagnostics."""

from custom_components.sony_bravia_ir.const import DOMAIN
from custom_components.sony_bravia_ir.diagnostics import (
    async_get_config_entry_diagnostics,
)
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .common import MockConfigEntry
from .conftest import (
    EMITTER_ENTITY_ID,
    RECEIVER_ENTITY_ID,
    MockInfraredEmitterEntity,
    MockInfraredReceiverEntity,
)


async def test_setup_and_unload(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test setting up and unloading a config entry."""
    assert init_integration.state is ConfigEntryState.LOADED
    assert hass.states.get("media_player.sony_bravia_tv") is not None
    assert hass.states.get("event.sony_bravia_tv_received_command") is not None

    assert await hass.config_entries.async_unload(init_integration.entry_id)
    await hass.async_block_till_done()
    assert init_integration.state is ConfigEntryState.NOT_LOADED


async def test_diagnostics(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test diagnostics return the entry data."""
    assert await async_get_config_entry_diagnostics(hass, init_integration) == {
        "generation": "android",
        "model": "KD-55X85J",
        "infrared_entity_id": EMITTER_ENTITY_ID,
        "infrared_receiver_entity_id": RECEIVER_ENTITY_ID,
    }


async def test_migrate_v1_to_v2(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
    mock_infrared_receiver_entity: MockInfraredReceiverEntity,
) -> None:
    """Test v1 entries (KDL-42W653A only) become classic entries with that model."""
    entry = MockConfigEntry(
        domain=DOMAIN, version=1, data={"infrared_entity_id": EMITTER_ENTITY_ID}
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.version == 2
    assert dict(entry.data) == {
        "infrared_entity_id": EMITTER_ENTITY_ID,
        "generation": "classic",
        "model": "KDL-42W653A",
    }
    entity_entry = er.async_get(hass).async_get("button.sony_bravia_tv_power")
    device = device_registry.async_get(entity_entry.device_id)
    assert device.model == "KDL-42W653A"
    # SEN is on the classic remote, so it is enabled.
    assert hass.states.get("button.sony_bravia_tv_sen") is not None


async def test_migrate_future_version_fails(hass: HomeAssistant) -> None:
    """Test entries from a newer version are not loaded."""
    entry = MockConfigEntry(domain=DOMAIN, version=3, data={})
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.MIGRATION_ERROR


async def test_device_model_defaults_to_bravia(
    hass: HomeAssistant,
    device_registry: dr.DeviceRegistry,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
) -> None:
    """Test the device model when none was entered."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        data={"generation": "android", "infrared_entity_id": EMITTER_ENTITY_ID},
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    entity_entry = er.async_get(hass).async_get("button.sony_bravia_tv_power")
    device = device_registry.async_get(entity_entry.device_id)
    assert device.model == "Bravia"
