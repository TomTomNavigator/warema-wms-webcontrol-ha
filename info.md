# Warema WMS WebControl for Home Assistant

This is a custom integration for Home Assistant that allows you to control your Warema WMS WebControl (the older WebControl, NOT WebControl Pro).

## Features

- **Covers**: Full support for Venetian blinds (Raffstores) and Awnings, including accurate position and tilt support.
- **Scenes**: Automatically extracts all your configured scenes (like "Alle Zu") and creates them as Home Assistant `button` entities.
- **Precise Tilt Control**: Generates a dedicated `number` entity for the tilt of each blind, mapped precisely to the real-world physical degree scale (-75° to +75°).

## Installation

### HACS (Recommended)
1. Go to HACS -> Integrations.
2. Click the three dots in the top right and select **Custom repositories**.
3. Add the URL of this repository and select **Integration** as the category.
4. Click **Download** to install.
5. Restart Home Assistant.

### Manual Installation
Copy the `custom_components/warema_wms_webcontrol` folder into your Home Assistant `config/custom_components` directory and restart Home Assistant.

## Configuration

Add the following to your `configuration.yaml` file, replacing the IP address with the local IP of your Warema WMS WebControl box:

```yaml
cover:
  - platform: warema_wms_webcontrol
    webcontrol_server_addr: "http://192.168.2.3"

button:
  - platform: warema_wms_webcontrol
    webcontrol_server_addr: "http://192.168.2.3"

number:
  - platform: warema_wms_webcontrol
    webcontrol_server_addr: "http://192.168.2.3"
```

Restart Home Assistant. Your devices will appear automatically!
