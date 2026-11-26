"""Constants for the Sony Bravia IR integration."""

from collections.abc import Mapping
from enum import StrEnum
from typing import Any

DOMAIN = "sony_bravia_ir"
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_INFRARED_RECEIVER_ENTITY_ID = "infrared_receiver_entity_id"
CONF_GENERATION = "generation"
CONF_MODEL = "model"
CONF_TRACK_PHYSICAL_REMOTE = "track_physical_remote"
DEFAULT_TRACK_PHYSICAL_REMOTE = True
# Update state: the media player keeps an assumed power and source state.
# When off it only sends commands, which also turns off following the
# physical remote.
CONF_UPDATE_STATE = "update_state"
DEFAULT_UPDATE_STATE = True
# Version 0.2.0 stored the opposite, as "stateless".
CONF_LEGACY_STATELESS = "stateless"


def update_state_enabled(options: Mapping[str, Any]) -> bool:
    """Return whether the media player keeps state, honouring 0.2.0 options."""
    if CONF_UPDATE_STATE in options:
        return bool(options[CONF_UPDATE_STATE])
    return not options.get(CONF_LEGACY_STATELESS, False)


# Dispatcher signal for keys received from the remote, formatted with the entry ID.
SIGNAL_RECEIVED_COMMAND = f"{DOMAIN}_received_command_{{}}"

MANUFACTURER = "Sony"
DEVICE_NAME = "Sony Bravia TV"


class BraviaGeneration(StrEnum):
    """Bravia remote generations, which differ in a few keys."""

    # Pre-2015 Bravia sets (KDL-...), remotes with SEN / Internet keys.
    CLASSIC = "classic"
    # 2015+ Android TV and Google TV sets (KD-/XR-...), remotes with app keys.
    ANDROID = "android"
