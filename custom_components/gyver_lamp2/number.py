"""Number platform for Gyver Lamp 2 settings."""
from __future__ import annotations
import logging

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import GyverLamp2Device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    
    numbers = [
        # Settings (Type 1) - Sliders
        GyverLamp2Number(device, "Brightness", "brightness", 0, 255, device.settings.get('brightness', 255), NumberMode.SLIDER, "mdi:brightness-6", "settings", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Min Brightness", "min_brightness", 0, 255, device.settings.get('min_brightness', 0), NumberMode.SLIDER, "mdi:brightness-1", "settings", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Max Brightness", "max_brightness", 0, 255, device.settings.get('max_brightness', 255), NumberMode.SLIDER, "mdi:brightness-7", "settings", EntityCategory.CONFIG),
        
        # Settings (Type 1) - Input fields
        GyverLamp2Number(device, "Max Current", "max_current", 0, 20000, device.settings.get('max_current', 500), NumberMode.BOX, "mdi:current-ac", "settings", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Work Hours From", "work_hours_from", 0, 23, device.settings.get('work_hours_from', 0), NumberMode.BOX, "mdi:clock-start", "settings", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Work Hours To", "work_hours_to", 0, 23, device.settings.get('work_hours_to', 23), NumberMode.BOX, "mdi:clock-end", "settings", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Matrix Length", "matrix_length", 0, 1000, device.settings.get('matrix_length', 16), NumberMode.BOX, "mdi:arrow-left-right", "settings", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Matrix Width", "matrix_width", 0, 1000, device.settings.get('matrix_width', 16), NumberMode.BOX, "mdi:arrow-up-down", "settings", EntityCategory.CONFIG),
        GyverLamp2Number(device, "City ID", "city_id", 0, 1000000, device.settings.get('city_id', 0), NumberMode.BOX, "mdi:map-marker", "settings", EntityCategory.CONFIG),
        
        # Preset Settings (Type 2) - Sliders
        GyverLamp2Number(device, "Preset Speed", "preset_speed", 0, 255, device.current_preset_config.get('speed', 128), NumberMode.SLIDER, "mdi:speedometer", "preset", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Preset Scale", "preset_scale", 0, 255, device.current_preset_config.get('scale', 255), NumberMode.SLIDER, "mdi:arrow-expand-all", "preset", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Preset Min Signal", "preset_min_signal", 0, 255, device.current_preset_config.get('min', 0), NumberMode.SLIDER, "mdi:volume-low", "preset", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Preset Max Signal", "preset_max_signal", 0, 255, device.current_preset_config.get('max', 255), NumberMode.SLIDER, "mdi:volume-high", "preset", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Preset Brightness", "preset_brightness", 0, 255, device.current_preset_config.get('bright', 255), NumberMode.SLIDER, "mdi:brightness-6", "preset", EntityCategory.CONFIG),
        GyverLamp2Number(device, "Preset Color", "preset_color", 0, 255, device.current_preset_config.get('color', 0), NumberMode.SLIDER, "mdi:palette", "preset", EntityCategory.CONFIG),
    ]
    async_add_entities(numbers)

class GyverLamp2Number(NumberEntity):
    """Number for device settings."""
    
    def __init__(self, device: GyverLamp2Device, name: str, unique_id_suffix: str, min_val: int, max_val: int, default_val: int, mode: NumberMode, icon: str, setting_type: str, entity_category: EntityCategory):
        """Initialize number."""
        self._device = device
        self._attr_name = name
        self._attr_unique_id = f"{device.entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = device.device_info
        self._attr_native_min_value = min_val
        self._attr_native_max_value = max_val
        self._attr_native_value = default_val
        self._attr_mode = mode
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_has_entity_name = True
        self._setting_key = unique_id_suffix
        self._setting_type = setting_type
        
        # Маппинг для пресетов (ИСПРАВЛЕНО)
        self._key_mapping = {
            'preset_speed': 'speed',
            'preset_scale': 'scale',
            'preset_min_signal': 'min', 
            'preset_max_signal': 'max',
            'preset_brightness': 'bright',
            'preset_color': 'color'
        }
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        if self._setting_type == "settings":
            self._attr_native_value = self._device.settings.get(self._setting_key, self._attr_native_value)
        elif self._setting_type == "preset":
            # Используем маппинг для пресетов
            preset_key = self._key_mapping.get(self._setting_key, self._setting_key.replace('preset_', ''))
            current_value = self._device.current_preset_config.get(preset_key, self._attr_native_value)
            self._attr_native_value = current_value
        self.async_write_ha_state()
    
    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = int(value)
        if self._setting_type == "settings":
            await self._device.set_setting(self._setting_key, int(value))
        elif self._setting_type == "preset":
            # Используем маппинг для пресетов
            preset_key = self._key_mapping.get(self._setting_key, self._setting_key.replace('preset_', ''))
            await self._device.update_current_preset({preset_key: int(value)})
        self.async_write_ha_state()