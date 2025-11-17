"""Sensor platform for Gyver Lamp 2."""
from __future__ import annotations
import logging

from homeassistant.components.sensor import SensorEntity
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
    """Set up the sensor platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    
    sensors = [
        GyverLamp2Sensor(device, "Port", "port", "port", "mdi:network-port", EntityCategory.DIAGNOSTIC),
        GyverLamp2Sensor(device, "Last Command", "last_command", "last_command", "mdi:code-braces", EntityCategory.DIAGNOSTIC),
        GyverLamp2Sensor(device, "Current Preset", "current_preset", "current_preset", "mdi:palette", EntityCategory.DIAGNOSTIC),
        GyverLamp2Sensor(device, "Presets Count", "presets_count", "presets_count", "mdi:counter", EntityCategory.DIAGNOSTIC),
        GyverLamp2Sensor(device, "Online Status", "online_status", "online_status", "mdi:lan-connect", EntityCategory.DIAGNOSTIC),
    ]
    async_add_entities(sensors)

class GyverLamp2Sensor(SensorEntity):
    """Sensor for device info."""
    
    def __init__(self, device: GyverLamp2Device, name: str, unique_id_suffix: str, sensor_type: str, icon: str, entity_category: EntityCategory):
        """Initialize sensor."""
        self._device = device
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"{device.entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = device.device_info
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_has_entity_name = True
        
        self._update_value()
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        self._update_value()
        self.async_write_ha_state()
    
    def _update_value(self):
        """Update sensor value based on type."""
        if self._sensor_type == "port":
            self._attr_native_value = self._device.port
        elif self._sensor_type == "last_command":
            self._attr_native_value = self._device.last_command
        elif self._sensor_type == "current_preset":
            self._attr_native_value = self._device.current_preset
        elif self._sensor_type == "presets_count":
            self._attr_native_value = len(self._device.presets)
        elif self._sensor_type == "online_status":
            # Простой статус - всегда онлайн, так как мы можем отправлять команды
            self._attr_native_value = "Online"
    
    async def async_update(self) -> None:
        """Update sensor value."""
        self._update_value()