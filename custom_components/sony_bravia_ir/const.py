"""Constants for the Sony Bravia IR integration."""

from enum import StrEnum

DOMAIN = "sony_bravia_ir"
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_INFRARED_RECEIVER_ENTITY_ID = "infrared_receiver_entity_id"
CONF_GENERATION = "generation"
CONF_MODEL = "model"
CONF_TRACK_PHYSICAL_REMOTE = "track_physical_remote"
DEFAULT_TRACK_PHYSICAL_REMOTE = True
# Stateless: the media player keeps no power or source state and only sends
# commands. This also turns off following the physical remote.
CONF_STATELESS = "stateless"
DEFAULT_STATELESS = False

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
