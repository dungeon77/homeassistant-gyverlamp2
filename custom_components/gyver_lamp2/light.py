"""Light platform for Gyver Lamp 2."""
from __future__ import annotations
import logging

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_CONTROL, CMD_ON, CMD_OFF
from .device import GyverLamp2Device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GyverLamp2Light(device)])

class GyverLamp2Light(LightEntity):
    """Representation of a Gyver Lamp 2 light."""
    
    _attr_has_entity_name = True
    
    def __init__(self, device: GyverLamp2Device):
        """Initialize the light."""
        self._device = device
        self._attr_name = "Light"
        self._attr_unique_id = f"{device.entry.entry_id}_light"
        self._attr_device_info = device.device_info
        self._attr_is_on = False
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        self.async_write_ha_state()
    
    async def async_turn_on(self, **kwargs):
        """Turn on the light."""
        await self._device.send_command(MODE_CONTROL, CMD_ON)
        self._attr_is_on = True
    
    async def async_turn_off(self, **kwargs):
        """Turn off the light."""
        await self._device.send_command(MODE_CONTROL, CMD_OFF)
        self._attr_is_on = False