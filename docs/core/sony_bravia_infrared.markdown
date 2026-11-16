---
title: Sony Bravia Infrared
description: Control a Sony Bravia TV with an infrared emitter and pick up key presses from its remote with an infrared receiver.
ha_category:
  - Media player
ha_release: 2026.12
ha_iot_class: Assumed State
ha_config_flow: true
ha_codeowners:
  - '@googanhiem'
ha_domain: sony_bravia_infrared
ha_integration_type: device
ha_platforms:
  - button
  - diagnostics
  - event
  - media_player
ha_quality_scale: gold
---

The **Sony Bravia Infrared** {% term integration %} lets you control a Sony Bravia TV using any infrared emitter you already have set up in Home Assistant. If you also have an infrared receiver, it picks up key presses from the Sony remote, so you can use the remote to run automations.

Infrared only goes one way. Commands are sent to the TV, but the TV never reports back, so Home Assistant can't tell whether it's on, which input it's on, or how loud it is. The integration uses assumed states.

If your Bravia is on your network, the [Sony Bravia TV](/integrations/braviatv/) integration can read the TV's real state and is usually the better choice. This integration is for sets that aren't on the network, or when you'd rather not use the network API.

## How you can use the integration

Once it's set up, you can control your TV from Home Assistant the same way you would with its remote, and use it in automations. For example, you can:

- Turn the TV off at bedtime, or when everyone leaves the house.
- Put the TV on a smart plug and turn it on as part of a movie scene.
- Use spare keys on the Sony remote, like the color keys, to control lights or run scenes.
- Build a dashboard remote with the navigation, home, and volume buttons.

## Supported devices

The integration works with Sony TVs that use the standard Sony infrared command set (12-bit SIRC on address 1). That covers Bravia sets from the older KDL models through current Android TV and Google TV models (KD, XR, and K series), and many older Sony TVs before them.

Bravia sets also understand a second group of codes (15-bit SIRC) for keys added later. The integration uses these for the discrete HDMI inputs and the playback keys.

Not every TV responds to every key. Older sets, for example, use **Enter** instead of **OK** to confirm a selection, and some older sets don't have the discrete HDMI or playback codes. The app shortcut keys on newer remotes aren't supported.

## Prerequisites

{% include integrations/infrared_controlled.md %}

To send commands, you need an infrared emitter pointed at the TV. To pick up key presses from your Sony remote, you also need an infrared receiver. For example, an ESPHome device with an IR LED and an IR receiver module can do both.

{% include integrations/config_flow.md %}

{% configuration_basic %}
Infrared emitter:
  description: "The infrared emitter entity used to send commands to your TV. It must come from a hardware integration (such as ESPHome) that is already set up with an IR emitter."
Infrared receiver:
  description: "The infrared receiver entity that picks up key presses from your Sony remote. It must come from a hardware integration (such as ESPHome) that is already set up with an IR receiver. Key presses show up as events you can use in automations."
{% endconfiguration_basic %}

Select at least one of **Infrared emitter** or **Infrared receiver**. Pick both if you want to send commands to the TV and react to the remote.

An infrared emitter or receiver can only be used by one Sony Bravia TV. To control a second TV, set it up with a different emitter.

## Reconfiguring the integration

If you replace your infrared emitter or add a receiver later, you can update the TV without removing and re-adding the integration.

1. Go to {% my integrations title="**Settings** > **Devices & services**" %}.
2. Find the **Sony Bravia Infrared** integration and select it.
3. Next to the TV you want to change, select the three dots {% icon "mdi:dots-vertical" %} menu and choose **Reconfigure**.
4. Change the options and select **Submit**.

You still need at least one infrared emitter or receiver. If you remove one of them, the entities that depend on it are no longer provided: the media player and buttons need an emitter, and the event entity needs a receiver. You can delete those entities from the entity settings.

## Supported functionality

### Media player

A media player entity is created when an infrared emitter is configured.

- **Sony Bravia TV**
  - **Description**: Represents the TV and controls it over infrared.
  - **Supported features**: Turn on, turn off, volume up, volume down, mute, next track (channel up), previous track (channel down), play, pause, stop, and select source.
  - **Sources**: **TV**, **HDMI 1**, **HDMI 2**, **HDMI 3**, **HDMI 4**.
  - **Remarks**: The TV never reports back, so the power state and source show the last command Home Assistant sent. They're kept across restarts. Using the physical remote doesn't update them.

### Buttons

Button entities are created when an infrared emitter is configured. Each button sends one key press to the TV.

These buttons are enabled by default:

- **Power**, **Power on**, **Power off**
- **HDMI 1**, **HDMI 2**, **HDMI 3**, **HDMI 4**
- **Play**, **Pause**, **Stop**
- **Volume up**, **Volume down**, **Mute**
- **Channel up**, **Channel down**
- **Input**
- **Up**, **Down**, **Left**, **Right**, **OK**
- **Home**, **Exit**, **Info**

These buttons are [disabled by default](/docs/configuration/customizing-entities/#disabling-or-enabling-an-entity), since they're less commonly used or not on every remote. Enable the ones you need.

- **Number 0** through **Number 9**, **Channel dash**, **Enter**
- **TV**, **HDMI**, **Component**
- **Red**, **Green**, **Yellow**, **Blue**
- **Rewind**, **Fast forward**, **Previous**, **Next**
- **Sleep**, **Jump**, **Favorites**, **Closed captions**, **Audio**, **Picture mode**

**Power** toggles the TV on or off, while **Power on** and **Power off** always do the same thing no matter what state the TV is in. **HDMI** and **Component** step through inputs of that type, while **HDMI 1** to **HDMI 4** go straight to that input.

### Events

An event entity is created when an infrared receiver is configured.

- **Received command**
  - **Description**: Fires when a key press from a Sony TV remote is picked up by the infrared receiver. The event type matches the key that was pressed.
  - **Event types**:
    - Power and volume: `power`, `power_on`, `power_off`, `mute`, `volume_up`, `volume_down`, `sleep`
    - Channels and inputs: `channel_up`, `channel_down`, `input`, `tv`, `hdmi`, `hdmi_1`, `hdmi_2`, `hdmi_3`, `hdmi_4`, `component`, `jump`, `favorites`
    - Playback: `play`, `pause`, `stop`, `rewind`, `fast_forward`, `previous`, `next`
    - Number keys: `num_0` through `num_9`, `channel_dash`, `enter`
    - Navigation: `nav_up`, `nav_down`, `nav_left`, `nav_right`, `ok`, `home`, `exit`, `info`
    - Picture and sound: `audio`, `picture`, `closed_captions`
    - Color keys: `red`, `green`, `yellow`, `blue`
    - `unknown` for any other Sony TV key
  - **Remarks**: Only Sony TV commands are processed. Signals from other remotes are ignored. Holding a key down fires a single event.

## Sony Bravia Infrared automation examples

For more ideas, see the media player [actions reference](/integrations/media_player/#list-of-actions).

{% include docs/paste_yaml_tip.md %}

### Automation: Toggling the lights with the red key on the TV remote

- **Trigger**: Event received
  - **Target**: Sony Bravia TV received command (`event.sony_bravia_tv_received_command`)
  - **Event type**: Red
- **Action**: Toggle light
  - **Target**: Living room (`light.living_room`)

{% details "YAML example for toggling the lights with the red key" %}

{% example %}
automation: |
  alias: "Toggle the living room lights with the red key"
  triggers:
    - trigger: event.received
      target:
        entity_id: event.sony_bravia_tv_received_command
      options:
        event_type:
          - red
  actions:
    - action: light.toggle
      target:
        entity_id: light.living_room
{% endexample %}

{% enddetails %}

### Automation: Switching to the game console when it turns on

- **Trigger**: Entity state changes to on
  - **Target**: Game console plug (`switch.game_console`)
- **Action**: Select source
  - **Target**: Sony Bravia TV (`media_player.sony_bravia_tv`)
  - **Source**: HDMI 2

{% details "YAML example for switching to the game console" %}

{% example %}
automation: |
  alias: "Switch the TV to the game console"
  triggers:
    - trigger: state
      entity_id: switch.game_console
      to: "on"
  actions:
    - action: media_player.turn_on
      target:
        entity_id: media_player.sony_bravia_tv
    - action: media_player.select_source
      target:
        entity_id: media_player.sony_bravia_tv
      data:
        source: HDMI 2
{% endexample %}

{% enddetails %}

### Automation: Turning the TV off when everyone leaves

- **Trigger**: Home becomes empty
  - **Target**: Home (`zone.home`)
- **Action**: Turn off media player
  - **Target**: Sony Bravia TV (`media_player.sony_bravia_tv`)

{% details "YAML example for turning the TV off when everyone leaves" %}

{% example %}
automation: |
  alias: "Turn off the TV when everyone leaves"
  triggers:
    - trigger: numeric_state
      entity_id: zone.home
      below: 1
  actions:
    - action: media_player.turn_off
      target:
        entity_id: media_player.sony_bravia_tv
{% endexample %}

{% enddetails %}

## Known limitations

- The media player uses assumed state. Home Assistant can't check what the TV is actually doing, and key presses from the physical remote show up as events only. They don't update the media player's power state or source.
- Volume is step-based only. You can't set an absolute volume level.
- Only **TV** and **HDMI 1** to **HDMI 4** can be selected as sources. There are no discrete codes for the other inputs.
- Playback keys only do something when the TV itself is playing media, like from USB or a built-in app. They don't control devices plugged in over HDMI unless the TV passes them on with HDMI-CEC (Bravia Sync).
- Quickly pressing the same key twice on the remote can show up as a single event, since a held key and a fast double press look the same to the receiver.

## Troubleshooting

### The TV doesn't respond to commands

If the entity changes in Home Assistant but the TV doesn't react, the infrared signal probably isn't reaching it. Make sure the emitter points at the TV's IR window and that nothing is in the way. For more steps, see [The device does not respond to commands](/connectivity/infrared/#the-device-does-not-respond-to-commands).

If the TV reacts to most buttons but not one or two, your model probably doesn't have those keys. Try **Enter** if **OK** does nothing. If **Power on** or the HDMI sources don't work on an older set, use **Power** and **Input** instead.

### The event entity doesn't fire when I press a key on the remote

The event entity only fires for Sony TV commands. Signals from other remotes, including universal remotes set to another brand, are ignored.

1. Make sure the TV has an infrared receiver selected. If it doesn't, add one by [reconfiguring the integration](#reconfiguring-the-integration).
2. Check that the infrared receiver entity updates when you press a key. If it doesn't, see [An infrared receiver does not pick up signals](/connectivity/infrared/#an-infrared-receiver-does-not-pick-up-signals).

### Reporting an issue

If you need to report an issue, enable [debug logging](/docs/configuration/troubleshooting/#debug-logs-and-diagnostics), then reload the integration. Reproduce the issue, disable debug logging, and attach the downloaded debug log to your report. Downloading the [diagnostics](/integrations/diagnostics/) for the TV helps too.

## Removing the integration

This integration follows standard integration removal.

{% include integrations/remove_device_service.md %}
