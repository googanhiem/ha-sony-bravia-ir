"""Button platform for the Sony Bravia IR integration."""

from dataclasses import dataclass
from typing import override

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .codes import SonyBraviaCode
from .const import CONF_GENERATION, CONF_INFRARED_ENTITY_ID, BraviaGeneration
from .entity import SonyBraviaIrEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class SonyBraviaIrButtonEntityDescription(ButtonEntityDescription):
    """Describes a Sony Bravia IR button entity."""

    command_code: SonyBraviaCode
    # Generations whose remote has this key; it is disabled by default on others.
    enabled_on: frozenset[BraviaGeneration]


_ALL = frozenset(BraviaGeneration)
_CLASSIC = frozenset({BraviaGeneration.CLASSIC})
_ANDROID = frozenset({BraviaGeneration.ANDROID})
_NONE: frozenset[BraviaGeneration] = frozenset()


def _button(
    key: str,
    code: SonyBraviaCode,
    *,
    enabled_on: frozenset[BraviaGeneration] = _ALL,
) -> SonyBraviaIrButtonEntityDescription:
    return SonyBraviaIrButtonEntityDescription(
        key=key,
        translation_key=key,
        command_code=code,
        enabled_on=enabled_on,
    )


BUTTON_DESCRIPTIONS: tuple[SonyBraviaIrButtonEntityDescription, ...] = (
    _button("power", SonyBraviaCode.POWER),
    _button("power_on", SonyBraviaCode.POWER_ON),
    _button("power_off", SonyBraviaCode.POWER_OFF),
    _button("input", SonyBraviaCode.INPUT),
    _button("tv", SonyBraviaCode.TV),
    _button("hdmi_1", SonyBraviaCode.HDMI_1),
    _button("hdmi_2", SonyBraviaCode.HDMI_2),
    _button("hdmi_3", SonyBraviaCode.HDMI_3),
    _button("hdmi_4", SonyBraviaCode.HDMI_4),
    _button("volume_up", SonyBraviaCode.VOLUME_UP),
    _button("volume_down", SonyBraviaCode.VOLUME_DOWN),
    _button("mute", SonyBraviaCode.MUTE),
    _button("channel_up", SonyBraviaCode.CHANNEL_UP),
    _button("channel_down", SonyBraviaCode.CHANNEL_DOWN),
    _button("home", SonyBraviaCode.HOME),
    _button("back", SonyBraviaCode.RETURN),
    _button("options", SonyBraviaCode.OPTIONS),
    _button("exit", SonyBraviaCode.EXIT),
    _button("info", SonyBraviaCode.DISPLAY),
    _button("guide", SonyBraviaCode.GUIDE),
    _button("sync_menu", SonyBraviaCode.SYNC_MENU),
    _button("sen", SonyBraviaCode.SEN, enabled_on=_CLASSIC),
    _button("netflix", SonyBraviaCode.NETFLIX, enabled_on=_ANDROID),
    _button("youtube", SonyBraviaCode.YOUTUBE, enabled_on=_ANDROID),
    _button("google_play", SonyBraviaCode.GOOGLE_PLAY, enabled_on=_ANDROID),
    _button("action_menu", SonyBraviaCode.ACTION_MENU, enabled_on=_ANDROID),
    _button("help", SonyBraviaCode.HELP, enabled_on=_NONE),
    _button("discover", SonyBraviaCode.DISCOVER, enabled_on=_NONE),
    _button("up", SonyBraviaCode.NAV_UP),
    _button("down", SonyBraviaCode.NAV_DOWN),
    _button("left", SonyBraviaCode.NAV_LEFT),
    _button("right", SonyBraviaCode.NAV_RIGHT),
    _button("ok", SonyBraviaCode.OK),
    _button("num_0", SonyBraviaCode.NUM_0),
    _button("num_1", SonyBraviaCode.NUM_1),
    _button("num_2", SonyBraviaCode.NUM_2),
    _button("num_3", SonyBraviaCode.NUM_3),
    _button("num_4", SonyBraviaCode.NUM_4),
    _button("num_5", SonyBraviaCode.NUM_5),
    _button("num_6", SonyBraviaCode.NUM_6),
    _button("num_7", SonyBraviaCode.NUM_7),
    _button("num_8", SonyBraviaCode.NUM_8),
    _button("num_9", SonyBraviaCode.NUM_9),
    _button("red", SonyBraviaCode.RED),
    _button("green", SonyBraviaCode.GREEN),
    _button("yellow", SonyBraviaCode.YELLOW),
    _button("blue", SonyBraviaCode.BLUE),
    _button("picture_mode", SonyBraviaCode.PICTURE_MODE),
    _button("picture_off", SonyBraviaCode.PICTURE_OFF, enabled_on=_NONE),
    _button("wide", SonyBraviaCode.WIDE),
    _button("audio", SonyBraviaCode.AUDIO),
    _button("subtitle", SonyBraviaCode.SUBTITLE),
    _button("teletext", SonyBraviaCode.TELETEXT, enabled_on=_CLASSIC),
    _button("jump", SonyBraviaCode.JUMP, enabled_on=_CLASSIC),
    _button("rewind", SonyBraviaCode.REWIND),
    _button("fast_forward", SonyBraviaCode.FAST_FORWARD),
    _button("previous", SonyBraviaCode.PREVIOUS),
    _button("next", SonyBraviaCode.NEXT),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Sony Bravia IR buttons from a config entry."""
    if not (infrared_entity_id := entry.data.get(CONF_INFRARED_ENTITY_ID)):
        return
    generation = BraviaGeneration(
        entry.data.get(CONF_GENERATION, BraviaGeneration.ANDROID)
    )
    async_add_entities(
        SonyBraviaIrButton(entry, infrared_entity_id, description, generation)
        for description in BUTTON_DESCRIPTIONS
    )


class SonyBraviaIrButton(
    SonyBraviaIrEntity, InfraredEmitterConsumerEntity, ButtonEntity
):
    """A single remote control key."""

    entity_description: SonyBraviaIrButtonEntityDescription

    def __init__(
        self,
        entry: ConfigEntry,
        infrared_entity_id: str,
        description: SonyBraviaIrButtonEntityDescription,
        generation: BraviaGeneration,
    ) -> None:
        """Initialize the button."""
        super().__init__(entry, unique_id_suffix=description.key)
        self._infrared_emitter_entity_id = infrared_entity_id
        self.entity_description = description
        self._attr_entity_registry_enabled_default = (
            generation in description.enabled_on
        )

    @override
    async def async_press(self) -> None:
        """Press the button."""
        await self._send_command(self.entity_description.command_code.to_command())
