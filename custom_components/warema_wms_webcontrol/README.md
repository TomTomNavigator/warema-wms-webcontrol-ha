# Warema WMS WebControl Integration for Home Assistant

A Custom Component for Home Assistant that provides local, polling-based control for Warema WMS sun shades (Raffstores / Blinds) using the Warema WMS WebControl hardware.

This integration automatically discovers your rooms and channels configured in the WebControl box and exposes them seamlessly to Home Assistant.

## Features

- **Covers**: Each sun shade is automatically added as a `cover` entity, allowing you to set the vertical position (0-100%).
- **Tilt / Angle (Neigung)**: Each sun shade also gets a dedicated `number` entity, representing the exact tilt of the slats in degrees (from -75° to 75°), exactly matching the Warema App!
- **Scenes**: All scenes programmed in the WMS WebControl are automatically exposed as `button` entities, which you can easily trigger from your dashboard or automations.
- **Robust Polling**: Built-in 10-minute fallback polling to sync manual remote control changes, plus rapid 15-second tracking when moving a cover via Home Assistant.
- **Hardware Protection**: Includes start-up delays and value-clamping to prevent overwhelming the older Warema WebControl hardware.

## Installation

### HACS (Recommended)
1. Open HACS in Home Assistant.
2. Go to **Integrations** -> **Custom repositories** (top right menu).
3. Add the URL of this repository and select **Integration** as category.
4. Click install and restart Home Assistant.

### Manual Installation
1. Download the `custom_components/warema_wms_webcontrol` folder from this repository.
2. Copy it into your Home Assistant's `custom_components/` directory.
3. Restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml` file:

```yaml
cover:
  - platform: warema_wms_webcontrol
    webcontrol_server_addr: "http://<IP_OF_YOUR_WEBCONTROL_BOX>"
    # update_interval: 600  (Optional: default is 600 seconds)

number:
  - platform: warema_wms_webcontrol
    webcontrol_server_addr: "http://<IP_OF_YOUR_WEBCONTROL_BOX>"

button:
  - platform: warema_wms_webcontrol
    webcontrol_server_addr: "http://<IP_OF_YOUR_WEBCONTROL_BOX>"
```

*Replace `<IP_OF_YOUR_WEBCONTROL_BOX>` with the actual IP address or hostname of your Warema WMS WebControl.*

Restart Home Assistant after adding the configuration.

## Dashboard Setup Recommendation

To get the perfect control experience (combining the standard position slider and the exact degree tilt slider), you can use the `slider-entity-row` custom card in your Lovelace Dashboard.

Example YAML for your dashboard:

```yaml
type: entities
title: Sonnenfeld Raffstores
entities:
  - type: section
    label: Wohnzimmer
  - type: custom:slider-entity-row
    entity: cover.sonnenfeld_wohnzimmer
    name: Position
    icon: mdi:window-shutter
    step: 1
  - type: custom:slider-entity-row
    entity: number.sonnenfeld_wohnzimmer_neigung
    name: Neigung (Tilt)
    icon: mdi:angle-acute
    step: 1
```
