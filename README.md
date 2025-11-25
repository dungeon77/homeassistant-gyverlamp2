# Gyver Lamp 2 Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Custom integration for Gyver Lamp 2 - WiFi RGB LED controller with UDP protocol support.

## Features

- ✅ **Full UDP protocol support** - Complete implementation of Gyver Lamp 2 protocol
- ✅ **Preset management** - Create, edit, delete and organize 25 presets
- ✅ **Real-time control** - Instant control via UDP broadcast
- ✅ **Group support** - Control multiple lamps in groups (1-8)
- ✅ **Comprehensive settings** - All lamp settings available in UI
- ✅ **Effect selection** - 7 built-in effects with custom parameters
- ✅ **Palette support** - 26 color palettes including custom
- ✅ **Sound reactivity** - Audio input and reaction settings
- ✅ **HA integration** - Native Home Assistant entities and UI

## Installation

### HACS (Recommended)
1. Open HACS in your Home Assistant
2. Go to "Integrations"
3. Click "+" and search for "Gyver Lamp 2"
4. Install the integration
5. Restart Home Assistant

### Manual
1. Copy the `gyver_lamp2` folder to `custom_components` in your Home Assistant config
2. Restart Home Assistant
3. Add integration via Settings → Devices & Services → Add Integration

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration" 
3. Search for "Gyver Lamp 2"
4. Enter your lamp details:
   - **IP Address**: Your network IP (e.g., 192.168.1.20)
   - **Network Key**: Default is "GL" (as in lamp firmware)
   - **Group Number**: 1-8 (for multiple lamp control)
   - **Device Name**: Custom name for your lamp

## Entities

### Control
- **Light** - On/Off control
- **Preset Select** - Choose from created presets
- **Group Select** - Switch between groups 1-8
- **Previous/Next Preset** - Quick preset navigation
- **Add/Delete/Reset Presets** - Preset management

### Settings
- **Brightness** - Global brightness control
- **Min/Max Brightness** - Brightness limits
- **Speed & Scale** - Effect parameters
- **Sound Reactivity** - Audio input settings
- **Palette Selection** - Color schemes
- **Matrix Settings** - LED matrix configuration
- **Timers & Schedules** - Auto on/off schedules

### Diagnostics
- **Port** - Current UDP port
- **Last Command** - Debug last sent command
- **Preset Count** - Number of created presets
- **Current Preset** - Active preset number

## Protocol Support

This integration implements the full UDP protocol:
- **Type 0**: Control commands (on/off, preset selection)
- **Type 1**: Device settings (brightness, timers, matrix)
- **Type 2**: Preset configurations (effects, palettes, parameters)

## Supported Effects
- 🌊 Perlin Noise
- 🎨 Solid Color  
- 🔄 Color Change
- 🌈 Gradient
- ✨ Particles
- 🔥 Fire
- ⛅ Weather

## Supported Palettes
- Custom, Thermal, Fire, Lava, Party, Rainbow, Clouds, Ocean, Forest, Sunset, Police, and 15 more!

## Troubleshooting

**Lamp not responding?**
- Check IP address format (e.g., 192.168.1.20)
- Verify network key matches lamp setting
- Ensure lamp is on same network segment

**Commands not working?**
- Check "Last Command" sensor for sent commands
- Verify UDP port calculation matches lamp group
- Ensure broadcast is enabled on your network

## Development

Based on official Gyver Lamp 2 firmware:
- GitHub: https://github.com/AlexGyver/GyverLamp2
- Protocol documentation in firmware source

## License

MIT License - see LICENSE file for details.

## Support

For issues and feature requests, please open an issue on GitHub:
https://github.com/dungeon77/homeassistant-gyverlamp2/issues
