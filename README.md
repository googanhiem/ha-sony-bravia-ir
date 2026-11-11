# Sony Bravia IR (KDL-42W653A) for Home Assistant

A Home Assistant custom integration that controls a **Sony Bravia KDL-42W653A**
TV over infrared. It is built the same way as Home Assistant's
[`lg_infrared`](https://github.com/home-assistant/core/tree/dev/homeassistant/components/lg_infrared)
integration. It sends commands through any entity from Home Assistant's
`infrared` integration (for example an ESPHome device with an IR LED) and can
listen to the original Sony remote through an infrared receiver.

## Requirements

- Home Assistant **2026.8** or newer (needs the `infrared` integration and its
  emitter/receiver helpers).
- At least one `infrared` emitter entity (to control the TV) and/or receiver
  entity (to react to the physical remote), e.g. from ESPHome.

## Installation

### HACS

1. HACS → ⋮ → *Custom repositories* → add this repository's URL, category **Integration**.
2. Install **Sony Bravia IR** and restart Home Assistant.

### Manual

Copy `custom_components/sony_bravia_ir` into your Home Assistant
`config/custom_components/` folder and restart.

## Setup

*Settings → Devices & services → Add integration → Sony Bravia IR*, then pick
an infrared emitter, a receiver, or both. You can change them later with
*Reconfigure*.

## Entities

All entities belong to one device, **Sony Bravia TV** (model KDL-42W653A).

| Platform | Entity | Needs |
| --- | --- | --- |
| `media_player` | `media_player.sony_bravia_tv`: on/off (discrete codes), volume step, mute, channel up/down (next/previous track), play/pause/stop, source select (TV, HDMI 1-4) | emitter |
| `button` | One button per remote key (53 in total, `netflix` and `picture_off` disabled by default) | emitter |
| `event` | `event.sony_bravia_tv_received_command`: fires with the key name when the original remote is used | receiver |

Infrared only sends; nothing reads back from the TV. Power state and source
are therefore *assumed* from the last command Home Assistant sent, and they
are restored after a restart. Using the original remote does not change the
media player state. Mute is a toggle on this TV.

### Automation example

```yaml
triggers:
  - trigger: state
    entity_id: event.sony_bravia_tv_received_command
    attribute: event_type
    to: red
actions:
  - action: light.toggle
    target:
      entity_id: light.living_room
```

## How the codes are sent

The TV uses Sony **SIRC**. Classic keys are 12-bit on address 1. Newer keys
(discrete HDMI inputs, transport, colour keys, Return/Options, Guide) are
15-bit on addresses `0x1A`, `0x97` and `0xA4`. Each command goes out as
**three identical frames**, because Sony TVs ignore a single frame. The
encoder uses `infrared_protocols.commands.sony.SonyCommand`. Decoding of
received signals is built in, so it works with every `infrared-protocols`
version that Home Assistant has shipped.

The table comes from the IRCC code list that 2013 Bravia models report over
their network API. Those IRCC codes are the same SIRC address/command pairs
the remote sends. If a key does not work on your set, open an issue with what
the `received_command` event reports for that key on your original remote.
That event includes the raw `address`, `address_bits` and `command`.

| Key | Format | Address | Command |
| --- | --- | --- | --- |
| `power` | 12-bit | `0x01` | `0x15` |
| `power_on` | 12-bit | `0x01` | `0x2E` |
| `power_off` | 12-bit | `0x01` | `0x2F` |
| `volume_up` | 12-bit | `0x01` | `0x12` |
| `volume_down` | 12-bit | `0x01` | `0x13` |
| `mute` | 12-bit | `0x01` | `0x14` |
| `channel_up` | 12-bit | `0x01` | `0x10` |
| `channel_down` | 12-bit | `0x01` | `0x11` |
| `input` | 12-bit | `0x01` | `0x25` |
| `tv` | 12-bit | `0x01` | `0x24` |
| `hdmi_1` | 15-bit | `0x1A` | `0x5A` |
| `hdmi_2` | 15-bit | `0x1A` | `0x5B` |
| `hdmi_3` | 15-bit | `0x1A` | `0x5C` |
| `hdmi_4` | 15-bit | `0x1A` | `0x5D` |
| `num_1` | 12-bit | `0x01` | `0x00` |
| `num_2` | 12-bit | `0x01` | `0x01` |
| `num_3` | 12-bit | `0x01` | `0x02` |
| `num_4` | 12-bit | `0x01` | `0x03` |
| `num_5` | 12-bit | `0x01` | `0x04` |
| `num_6` | 12-bit | `0x01` | `0x05` |
| `num_7` | 12-bit | `0x01` | `0x06` |
| `num_8` | 12-bit | `0x01` | `0x07` |
| `num_9` | 12-bit | `0x01` | `0x08` |
| `num_0` | 12-bit | `0x01` | `0x09` |
| `nav_up` | 12-bit | `0x01` | `0x74` |
| `nav_down` | 12-bit | `0x01` | `0x75` |
| `nav_left` | 12-bit | `0x01` | `0x34` |
| `nav_right` | 12-bit | `0x01` | `0x33` |
| `ok` | 12-bit | `0x01` | `0x65` |
| `home` | 12-bit | `0x01` | `0x60` |
| `return` | 15-bit | `0x97` | `0x23` |
| `options` | 15-bit | `0x97` | `0x36` |
| `exit` | 12-bit | `0x01` | `0x63` |
| `display` | 12-bit | `0x01` | `0x3A` |
| `guide` | 15-bit | `0xA4` | `0x5B` |
| `sync_menu` | 15-bit | `0x1A` | `0x58` |
| `sen` | 15-bit | `0x1A` | `0x7D` |
| `netflix` | 15-bit | `0x1A` | `0x7C` |
| `red` | 15-bit | `0x97` | `0x25` |
| `green` | 15-bit | `0x97` | `0x26` |
| `yellow` | 15-bit | `0x97` | `0x27` |
| `blue` | 15-bit | `0x97` | `0x24` |
| `picture_mode` | 12-bit | `0x01` | `0x64` |
| `picture_off` | 12-bit | `0x01` | `0x3E` |
| `wide` | 15-bit | `0xA4` | `0x3D` |
| `audio` | 12-bit | `0x01` | `0x17` |
| `subtitle` | 15-bit | `0x97` | `0x28` |
| `teletext` | 12-bit | `0x01` | `0x3F` |
| `jump` | 12-bit | `0x01` | `0x3B` |
| `play` | 15-bit | `0x97` | `0x1A` |
| `pause` | 15-bit | `0x97` | `0x19` |
| `stop` | 15-bit | `0x97` | `0x18` |
| `rewind` | 15-bit | `0x97` | `0x1B` |
| `fast_forward` | 15-bit | `0x97` | `0x1C` |
| `previous` | 15-bit | `0x97` | `0x3C` |
| `next` | 15-bit | `0x97` | `0x3D` |

## Development

```bash
uv venv --python 3.14 .venv
uv pip install --python .venv -r requirements_test.txt
.venv/bin/pytest
```

## License

MIT
