"""Tests for the Sony Bravia IR config flow."""

import pytest

from custom_components.sony_bravia_ir.const import (
    CONF_GENERATION,
    CONF_INFRARED_ENTITY_ID,
    CONF_INFRARED_RECEIVER_ENTITY_ID,
    CONF_MODEL,
    CONF_TRACK_PHYSICAL_REMOTE,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from .common import MockConfigEntry
from .conftest import EMITTER_ENTITY_ID, RECEIVER_ENTITY_ID

pytestmark = pytest.mark.usefixtures(
    "mock_infrared_emitter_entity", "mock_infrared_receiver_entity"
)


@pytest.mark.parametrize(
    ("user_input", "expected_title"),
    [
        pytest.param(
            {CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID},
            "Sony Bravia TV via Test IR emitter",
            id="emitter_only",
        ),
        pytest.param(
            {
                CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID,
                CONF_INFRARED_RECEIVER_ENTITY_ID: RECEIVER_ENTITY_ID,
            },
            "Sony Bravia TV via Test IR emitter",
            id="emitter_and_receiver",
        ),
        pytest.param(
            {CONF_INFRARED_RECEIVER_ENTITY_ID: RECEIVER_ENTITY_ID},
            "Sony Bravia TV via Test IR receiver",
            id="receiver_only",
        ),
    ],
)
async def test_user_flow(
    hass: HomeAssistant, user_input: dict[str, str], expected_title: str
) -> None:
    """Test a successful user flow."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=user_input
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == expected_title
    # The generation defaults to Android TV / Google TV.
    assert result["data"] == {CONF_GENERATION: "android", **user_input}


async def test_user_flow_with_model(hass: HomeAssistant) -> None:
    """Test the model and generation end up in the entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    user_input = {
        CONF_GENERATION: "classic",
        CONF_MODEL: "KDL-42W653A",
        CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID,
    }
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=user_input
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Sony Bravia KDL-42W653A via Test IR emitter"
    assert result["data"] == user_input
    assert result["result"].version == 2


async def test_user_flow_requires_entity(hass: HomeAssistant) -> None:
    """Test the flow errors when nothing is selected."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "missing_infrared_entity"}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


@pytest.mark.parametrize(
    "user_input",
    [
        {CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID},
        {CONF_INFRARED_RECEIVER_ENTITY_ID: RECEIVER_ENTITY_ID},
    ],
)
async def test_user_flow_already_configured(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    user_input: dict[str, str],
) -> None:
    """Test the flow aborts when an IR entity is already used."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=user_input
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("init_infrared")
async def test_reconfigure_keeps_same_entities(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test reconfiguring with the same emitter does not abort as duplicate."""
    result = await init_integration.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input={
            CONF_GENERATION: "classic",
            CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID,
        },
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    # The cleared receiver and model are removed from the entry.
    assert dict(init_integration.data) == {
        CONF_GENERATION: "classic",
        CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID,
    }


async def test_reconfigure_requires_entity(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test reconfigure errors when nothing is selected."""
    result = await init_integration.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "missing_infrared_entity"}


async def test_reconfigure_duplicate(
    hass: HomeAssistant, init_integration: MockConfigEntry
) -> None:
    """Test reconfigure aborts when another entry uses the emitter."""
    other = MockConfigEntry(
        domain=DOMAIN,
        version=2,
        data={CONF_GENERATION: "android", CONF_INFRARED_ENTITY_ID: "infrared.other"},
    )
    other.add_to_hass(hass)
    result = await other.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_no_infrared_entities(hass: HomeAssistant) -> None:
    """Test the flow aborts when there are no IR entities."""
    for entity_id in (EMITTER_ENTITY_ID, RECEIVER_ENTITY_ID):
        await hass.data["infrared"].async_remove_entity(entity_id)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_infrared_entities"


@pytest.mark.parametrize("track_physical_remote", [False, True])
async def test_options_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    track_physical_remote: bool,
) -> None:
    """Test turning physical remote tracking on and off."""
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_TRACK_PHYSICAL_REMOTE: track_physical_remote},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {
        "update_state": True,
        CONF_TRACK_PHYSICAL_REMOTE: track_physical_remote,
    }


@pytest.mark.parametrize("has_receiver", [False])
async def test_options_flow_without_receiver(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test only Update state is offered when no receiver is configured."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert CONF_TRACK_PHYSICAL_REMOTE not in result["data_schema"].schema
    assert "update_state" in result["data_schema"].schema

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"update_state": False}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == {"update_state": False}
