"""Media player platform for the Sony Bravia IR integration."""

from typing import override

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .codes import SonyBraviaCode
from .const import CONF_INFRARED_ENTITY_ID, DOMAIN
from .entity import SonyBraviaIrEntity

PARALLEL_UPDATES = 1

SOURCE_TO_CODE: dict[str, SonyBraviaCode] = {
    "TV": SonyBraviaCode.TV,
    "HDMI 1": SonyBraviaCode.HDMI_1,
    "HDMI 2": SonyBraviaCode.HDMI_2,
    "HDMI 3": SonyBraviaCode.HDMI_3,
    "HDMI 4": SonyBraviaCode.HDMI_4,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Sony Bravia IR media player from a config entry."""
    if not (infrared_entity_id := entry.data.get(CONF_INFRARED_ENTITY_ID)):
        return
    async_add_entities([SonyBraviaIrMediaPlayer(entry, infrared_entity_id)])


class SonyBraviaIrMediaPlayer(
    SonyBraviaIrEntity, InfraredEmitterConsumerEntity, MediaPlayerEntity, RestoreEntity
):
    """Sony Bravia TV controlled over infrared.

    Infrared is one-way, so power state and source are assumed from the last
    command sent and restored across restarts.
    """

    _attr_name = None
    _attr_assumed_state = True
    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_supported_features = (
        MediaPlayerEntityFeature.TURN_ON
        | MediaPlayerEntityFeature.TURN_OFF
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.NEXT_TRACK
        | MediaPlayerEntityFeature.PREVIOUS_TRACK
        | MediaPlayerEntityFeature.PLAY
        | MediaPlayerEntityFeature.PAUSE
        | MediaPlayerEntityFeature.STOP
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, entry: ConfigEntry, infrared_entity_id: str) -> None:
        """Initialize the media player."""
        super().__init__(entry, unique_id_suffix="media_player")
        self._infrared_emitter_entity_id = infrared_entity_id
        self._attr_state = MediaPlayerState.ON
        self._attr_source = None
        self._attr_source_list = list(SOURCE_TO_CODE)

    @override
    async def async_added_to_hass(self) -> None:
        """Restore the assumed power state and source."""
        await super().async_added_to_hass()
        if (last_state := await self.async_get_last_state()) is None:
            return
        if last_state.state == MediaPlayerState.OFF:
            self._attr_state = MediaPlayerState.OFF
        if (source := last_state.attributes.get("source")) in SOURCE_TO_CODE:
            self._attr_source = source

    async def _send(self, code: SonyBraviaCode) -> None:
        """Send a code to the TV."""
        await self._send_command(code.to_command())

    @override
    async def async_turn_on(self) -> None:
        """Turn on the TV."""
        await self._send(SonyBraviaCode.POWER_ON)
        self._attr_state = MediaPlayerState.ON
        self.async_write_ha_state()

    @override
    async def async_turn_off(self) -> None:
        """Turn off the TV."""
        await self._send(SonyBraviaCode.POWER_OFF)
        self._attr_state = MediaPlayerState.OFF
        self.async_write_ha_state()

    @override
    async def async_volume_up(self) -> None:
        """Send volume up."""
        await self._send(SonyBraviaCode.VOLUME_UP)

    @override
    async def async_volume_down(self) -> None:
        """Send volume down."""
        await self._send(SonyBraviaCode.VOLUME_DOWN)

    @override
    async def async_mute_volume(self, mute: bool) -> None:
        """Toggle mute (the TV only has a mute toggle)."""
        await self._send(SonyBraviaCode.MUTE)

    @override
    async def async_media_next_track(self) -> None:
        """Send channel up."""
        await self._send(SonyBraviaCode.CHANNEL_UP)

    @override
    async def async_media_previous_track(self) -> None:
        """Send channel down."""
        await self._send(SonyBraviaCode.CHANNEL_DOWN)

    @override
    async def async_media_play(self) -> None:
        """Send play."""
        await self._send(SonyBraviaCode.PLAY)

    @override
    async def async_media_pause(self) -> None:
        """Send pause."""
        await self._send(SonyBraviaCode.PAUSE)

    @override
    async def async_media_stop(self) -> None:
        """Send stop."""
        await self._send(SonyBraviaCode.STOP)

    @override
    async def async_select_source(self, source: str) -> None:
        """Switch to an input using its discrete code."""
        if (code := SOURCE_TO_CODE.get(source)) is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_source",
                translation_placeholders={"source": source},
            )
        await self._send(code)
        self._attr_source = source
        self.async_write_ha_state()
