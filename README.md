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

This integration supports setup via the Home Assistant UI (Config Flow):

1. Go to **Settings** -> **Devices & Services** in Home Assistant.
2. Click **+ Add Integration** in the bottom right corner.
3. Search for **Warema WMS WebControl** and click on it.
4. Enter the URL/IP address of your WebControl gateway (e.g., `http://192.168.2.3`).
5. (Optional) Adjust the update interval if needed.
6. Click **Submit**.

Your shades and scenes will automatically be discovered and added as devices/entities!

*(Note: Legacy setup via `configuration.yaml` is still supported as a fallback, but UI setup is highly recommended).*
