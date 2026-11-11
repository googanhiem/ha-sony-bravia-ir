"""Constants for the Sony Bravia IR integration."""

from enum import StrEnum

DOMAIN = "sony_bravia_ir"
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_INFRARED_RECEIVER_ENTITY_ID = "infrared_receiver_entity_id"
CONF_GENERATION = "generation"
CONF_MODEL = "model"

MANUFACTURER = "Sony"
DEVICE_NAME = "Sony Bravia TV"


class BraviaGeneration(StrEnum):
    """Bravia remote generations, which differ in a few keys."""

    # Pre-2015 Bravia sets (KDL-...), remotes with SEN / Internet keys.
    CLASSIC = "classic"
    # 2015+ Android TV and Google TV sets (KD-/XR-...), remotes with app keys.
    ANDROID = "android"
