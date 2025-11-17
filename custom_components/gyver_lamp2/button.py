"""Button platform for Gyver Lamp 2."""
from __future__ import annotations
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_CONTROL, CMD_PREV_PRESET, CMD_NEXT_PRESET, CMD_REBOOT
from .device import GyverLamp2Device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    
    buttons = [
        # Управление (None category)
        GyverLamp2Button(device, "Previous Preset", "prev_preset", CMD_PREV_PRESET, "mdi:skip-previous", None),
        GyverLamp2Button(device, "Next Preset", "next_preset", CMD_NEXT_PRESET, "mdi:skip-next", None),
        GyverLamp2Button(device, "Add Preset", "add_preset", "add_preset", "mdi:plus-box", None),
        GyverLamp2Button(device, "Delete Last Preset", "delete_preset", "delete_preset", "mdi:minus-box", None),
        GyverLamp2Button(device, "Reset Presets", "reset_presets", "reset_presets", "mdi:refresh", None),
        GyverLamp2Button(device, "Reboot Lamp", "reboot", CMD_REBOOT, "mdi:restart", None),
        
        # Настройки (CONFIG category)
        GyverLamp2Button(device, "Upload Settings", "upload_settings", "upload_settings", "mdi:upload", "config"),
    ]
    async_add_entities(buttons)

class GyverLamp2Button(ButtonEntity):
    """Button to change presets."""
    
    def __init__(self, device: GyverLamp2Device, name: str, unique_id_suffix: str, command, icon: str, entity_category):
        """Initialize button."""
        self._device = device
        self._command = command
        self._attr_name = name
        self._attr_unique_id = f"{device.entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = device.device_info
        self._attr_icon = icon
        self._attr_has_entity_name = True
        
        if entity_category == "config":
            from homeassistant.helpers.entity import EntityCategory
            self._attr_entity_category = EntityCategory.CONFIG
        else:
            self._attr_entity_category = None
    
    async def async_press(self) -> None:
        """Handle the button press."""
        if self._command in [CMD_PREV_PRESET, CMD_NEXT_PRESET, CMD_REBOOT]:
            await self._device.send_command(MODE_CONTROL, self._command)
        elif self._command == "add_preset":
            await self._device.add_preset()
        elif self._command == "delete_preset":
            await self._device.delete_last_preset()
        elif self._command == "reset_presets":
            await self._device.reset_presets()
        elif self._command == "upload_settings":
            await self._device.send_settings_command(self._device.settings)