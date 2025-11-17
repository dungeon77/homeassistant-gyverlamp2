"""Text platform for Gyver Lamp 2."""
from __future__ import annotations
import logging

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NETWORK_KEY, DEFAULT_KEY
from .device import GyverLamp2Device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the text platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    
    texts = [
        GyverLamp2Text(device, "Network Key", "network_key", 
                      device.config.get(CONF_NETWORK_KEY, DEFAULT_KEY),
                      "mdi:key", EntityCategory.CONFIG),
    ]
    async_add_entities(texts)

class GyverLamp2Text(TextEntity):
    """Text entity for network key."""
    
    def __init__(self, device: GyverLamp2Device, name: str, unique_id_suffix: str, default_value: str, icon: str, entity_category: EntityCategory):
        """Initialize text."""
        self._device = device
        self._attr_name = name
        self._attr_unique_id = f"{device.entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = device.device_info
        self._attr_native_value = default_value
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_has_entity_name = True
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        # Обновляем значение из конфига
        self._attr_native_value = self._device.config.get(CONF_NETWORK_KEY, DEFAULT_KEY)
        self.async_write_ha_state()
    
    async def async_set_value(self, value: str) -> None:
        """Update the current value."""
        self._attr_native_value = value
        
        # Обновляем конфиг
        new_data = {**self._device.entry.data, CONF_NETWORK_KEY: value}
        self._device.hass.config_entries.async_update_entry(
            self._device.entry, data=new_data
        )
        
        # Пересчитываем порт
        self._device.port = self._device._calculate_port()
        
        self.async_write_ha_state()
    
    @property
    def native_min(self) -> int:
        """Return the minimum length."""
        return 1
    
    @property
    def native_max(self) -> int:
        """Return the maximum length."""
        return 32
    
    @property
    def pattern(self) -> str | None:
        """Return the pattern for the text."""
        return None