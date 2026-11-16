# Core port: sony_bravia_infrared

Files for getting this integration into Home Assistant core.

- `0001-Add-Sony-Bravia-Infrared-integration.patch`: the core commit. Made against
  core `dev` at 7eae24db.
- `sony_bravia_infrared.markdown`: draft docs page for home-assistant.io
  (`source/_integrations/`).

To apply it to your fork of core:

```bash
git checkout -b sony_bravia_infrared upstream/dev
git am /path/to/0001-Add-Sony-Bravia-Infrared-integration.patch
```
