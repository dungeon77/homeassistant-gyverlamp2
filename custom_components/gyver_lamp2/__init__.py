"""The Gyver Lamp 2 integration."""
from __future__ import annotations
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .device import GyverLamp2Device

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["light", "button", "sensor", "select", "number", "switch"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create device instance
    device = GyverLamp2Device(hass, entry)
    
    # Load settings from storage
    await device.async_load_settings()
    
    hass.data[DOMAIN][entry.entry_id] = device
    
    # Setup all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload integration."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok