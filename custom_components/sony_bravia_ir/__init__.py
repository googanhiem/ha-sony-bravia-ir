"""Sony Bravia IR integration for Home Assistant."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_GENERATION, CONF_MODEL, BraviaGeneration

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BUTTON,
    Platform.EVENT,
    Platform.MEDIA_PLAYER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sony Bravia IR from a config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Sony Bravia IR config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old config entries."""
    if entry.version > 2:
        return False
    if entry.version == 1:
        # v1 only supported the KDL-42W653A.
        _LOGGER.debug("Migrating config entry from version 1 to 2")
        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_GENERATION: BraviaGeneration.CLASSIC,
                CONF_MODEL: "KDL-42W653A",
            },
            version=2,
        )
    return True
