"""Switch platform for Gyver Lamp 2 settings."""
from __future__ import annotations
import logging

from homeassistant.components.switch import SwitchEntity
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
    """Set up the switch platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    
    switches = [
        # Управление (None category) - Random Order теперь в управлении
        GyverLamp2Switch(device, "Random Order", "random_order", 
                        device.settings.get('random_order', 0) == 1, 
                        "mdi:shuffle", "settings", None),
        
        # Настройки (CONFIG category)
        GyverLamp2Switch(device, "Preset Reduce Brightness", "preset_reduce_brightness", 
                        device.current_preset_config.get('fadeBright', 0) == 1, 
                        "mdi:brightness-percent", "preset", EntityCategory.CONFIG),
        GyverLamp2Switch(device, "Preset From Center", "preset_from_center", 
                        device.current_preset_config.get('fromCenter', 0) == 1, 
                        "mdi:ray-vertex", "preset", EntityCategory.CONFIG),
        GyverLamp2Switch(device, "Preset From Palette", "preset_from_palette", 
                        device.current_preset_config.get('fromPal', 0) == 1, 
                        "mdi:palette", "preset", EntityCategory.CONFIG),
    ]
    async_add_entities(switches)

class GyverLamp2Switch(SwitchEntity):
    """Switch for device settings."""
    
    def __init__(self, device: GyverLamp2Device, name: str, unique_id_suffix: str, default_state: bool, icon: str, setting_type: str, entity_category):
        """Initialize switch."""
        self._device = device
        self._attr_name = name
        self._attr_unique_id = f"{device.entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = device.device_info
        self._attr_is_on = default_state
        self._attr_icon = icon
        self._attr_has_entity_name = True
        self._setting_key = unique_id_suffix
        self._setting_type = setting_type
        
        # Маппинг для пресетов (ИСПРАВЛЕНО)
        self._key_mapping = {
            'preset_reduce_brightness': 'fadeBright',
            'preset_from_center': 'fromCenter',
            'preset_from_palette': 'fromPal'
        }
        
        if entity_category == "config":
            from homeassistant.helpers.entity import EntityCategory
            self._attr_entity_category = EntityCategory.CONFIG
        else:
            self._attr_entity_category = entity_category
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        if self._setting_type == "settings":
            self._attr_is_on = self._device.settings.get(self._setting_key, 0) == 1
        elif self._setting_type == "preset":
            # Используем маппинг для пресетов
            preset_key = self._key_mapping.get(self._setting_key, self._setting_key.replace('preset_', ''))
            self._attr_is_on = self._device.current_preset_config.get(preset_key, 0) == 1
        self.async_write_ha_state()
    
    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        self._attr_is_on = True
        if self._setting_type == "settings":
            await self._device.set_setting(self._setting_key, 1)
        elif self._setting_type == "preset":
            # Используем маппинг для пресетов
            preset_key = self._key_mapping.get(self._setting_key, self._setting_key.replace('preset_', ''))
            await self._device.update_current_preset({preset_key: 1})
        self.async_write_ha_state()
    
    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        self._attr_is_on = False
        if self._setting_type == "settings":
            await self._device.set_setting(self._setting_key, 0)
        elif self._setting_type == "preset":
            # Используем маппинг для пресетов
            preset_key = self._key_mapping.get(self._setting_key, self._setting_key.replace('preset_', ''))
            await self._device.update_current_preset({preset_key: 0})
        self.async_write_ha_state()