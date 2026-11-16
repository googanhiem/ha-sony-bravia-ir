# Core port: sony_bravia_infrared

Files for getting this integration into Home Assistant core.

- `infrared-protocols/`: the library change. Adds `POWER_ON` and `POWER_OFF`
  to `SonyTVCode`, a new `SonyTVExtendedCode` table (HDMI 1 to 4 and the
  playback keys, 15-bit SIRC), and a `repeat_count` argument on both tables'
  `to_command()`. Made against infrared-protocols `main` at 78e998b.
- `core/`: the core commits. Made against core `dev` at 7eae24db. Patch 0002
  needs the library change above.
- `sony_bravia_infrared.markdown`: draft docs page for home-assistant.io
  (`source/_integrations/`).

## Order

The library template requires a linked draft core PR, and core can only pin a
released library version. So:

1. Open the core PR as a draft from your fork.
2. Open the infrared-protocols PR and link the draft core PR.
3. After the library is released, bump `infrared-protocols` in
   `homeassistant/components/infrared/manifest.json` (core wants that bump as
   its own PR), then mark the core PR ready for review.

Until step 3, core CI will fail on the core PR, because core still pins
infrared-protocols 10.7.0.

## Applying the patches

In your fork of infrared-protocols:

```bash
git checkout -b sony-tv-extended-codes origin/main
```

```bash
git am /path/to/docs/core/infrared-protocols/*.patch
```

In your fork of core:

```bash
git checkout -b sony_bravia_infrared upstream/dev
```

```bash
git am /path/to/docs/core/core/*.patch
```

## Provenance of the new codes

PR #134 asked for at least three source remotes per code. These sources were
checked:

- **IRCC**: Sony's own IRCC table for Bravia displays
  (pro-bravia.sony.net, "IRCC-IP"), which is the same data sets report over
  `getRemoteControllerInfo`.
- **IRDB**: probonopd/irdb, `codes/Sony/TV/` (`1,-1`, `26,-1`, `151,-1`).
- **LIRC**: lirc-remotes, `remotes/sony/`.
- **pybravia**: `CODE_POWER_ON` in pybravia's `const.py`, which core's
  braviatv integration uses.

| Code | Address / bits | Command | Sources |
| --- | --- | --- | --- |
| POWER_ON | 0x01 / 5 | 0x2E | IRDB, LIRC RM-Y103, pybravia |
| POWER_OFF | 0x01 / 5 | 0x2F | IRDB, LIRC RM-Y103 |
| HDMI_1 to HDMI_4 | 0x1A / 8 | 0x5A to 0x5D | IRCC, IRDB |
| PLAY | 0x97 / 8 | 0x1A | IRCC, IRDB, LIRC RM-ED035, RM-YD010 |
| PAUSE | 0x97 / 8 | 0x19 | IRCC, IRDB, LIRC RM-YD010 |
| STOP | 0x97 / 8 | 0x18 | IRCC, IRDB, LIRC RM-ED035, RM-YD010 |
| REWIND | 0x97 / 8 | 0x1B | IRDB, LIRC RM-ED035, RM-YD010 |
| FAST_FORWARD | 0x97 / 8 | 0x1C | IRDB, LIRC RM-ED035, RM-YD010 |
| PREVIOUS | 0x97 / 8 | 0x3C | IRCC, IRDB, LIRC RM-ED035, RM-YD010 |
| NEXT | 0x97 / 8 | 0x3D | IRCC, IRDB, LIRC RM-ED035, RM-YD010 |

POWER_OFF and HDMI 1 to 4 only have two independent sources here. Testing them
on your own sets, and naming those models in the PR, is the best way to make
up the gap.
