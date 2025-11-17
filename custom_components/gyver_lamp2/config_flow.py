"""Config flow for Gyver Lamp 2."""
from __future__ import annotations
import voluptuous as vol
import socket
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.util.network import is_ip_address

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_KEY,
    DEFAULT_GROUP,
    CONF_IP_ADDRESS,
    CONF_NETWORK_KEY,
    CONF_GROUP_NUMBER,
    CONF_NAME
)

def get_default_ip() -> str:
    """Get default IP based on host IP."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ha_ip = s.getsockname()[0]
        s.close()
        if is_ip_address(ha_ip):
            return ".".join(ha_ip.split(".")[:3]) + "."
    except Exception:
        pass
    return "192.168.31."

class GyverLamp2ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gyver Lamp 2."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            ip = user_input[CONF_IP_ADDRESS]
            if not (ip.endswith(".") or is_ip_address(ip)):
                errors[CONF_IP_ADDRESS] = "invalid_ip"
            else:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(
                    CONF_IP_ADDRESS,
                    default=get_default_ip()
                ): str,
                vol.Required(
                    CONF_NETWORK_KEY,
                    default=DEFAULT_KEY
                ): str,
                vol.Required(
                    CONF_GROUP_NUMBER,
                    default=DEFAULT_GROUP
                ): int,
                vol.Optional(
                    CONF_NAME,
                    default=DEFAULT_NAME
                ): str,
            }),
            errors=errors
        )