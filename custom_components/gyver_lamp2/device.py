"""Device management."""
from __future__ import annotations
import logging
import socket
import asyncio
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.storage import Store

from .const import DOMAIN, DEFAULT_NAME, CONF_NAME, EFFECTS, PALETTES

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1
STORAGE_KEY = f"{DOMAIN}.storage"

class GyverLamp2Device:
    """Main device class."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        self.hass = hass
        self.entry = entry
        self.config = entry.data
        
        # Инициализация хранилища
        self._store = Store(hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.entry_id}")
        
        # Инициализация данных
        self._settings = self._get_default_settings()
        self._presets = [self._create_default_preset(1)]
        self._current_preset = 1
        self._current_group = self.config["group_number"]
        
        self._last_command = None
        self._listeners = []
        
        # Calculate initial port
        self.port = self._calculate_port()
        self.ip = self._get_broadcast_ip()
    
    async def async_load_settings(self):
        """Load settings from storage."""
        try:
            data = await self._store.async_load()
            if data:
                self._settings = data.get('settings', self._get_default_settings())
                self._presets = data.get('presets', [self._create_default_preset(1)])
                self._current_preset = data.get('current_preset', 1)
                self._current_group = data.get('current_group', self.config["group_number"])
                _LOGGER.debug("Settings loaded from storage")
            else:
                await self._async_save_settings()
                _LOGGER.debug("Initial settings saved to storage")
        except Exception as e:
            _LOGGER.error(f"Error loading settings from storage: {e}")
            await self._async_save_settings()
    
    async def _async_save_settings(self):
        """Save settings to storage."""
        try:
            data = {
                'settings': self._settings,
                'presets': self._presets,
                'current_preset': self._current_preset,
                'current_group': self._current_group
            }
            await self._store.async_save(data)
            _LOGGER.debug("Settings saved to storage")
        except Exception as e:
            _LOGGER.error(f"Error saving settings to storage: {e}")
    
    def _get_default_settings(self) -> dict:
        """Get default settings."""
        return {
            'brightness': 255,
            'adc_mode': 1,
            'min_brightness': 0,
            'max_brightness': 255,
            'mode_change': 0,
            'random_order': 0,
            'change_period': 1,
            'lamp_type': 1,
            'max_current': 500,
            'work_hours_from': 0,
            'work_hours_to': 23,
            'matrix_orientation': 1,
            'matrix_length': 16,
            'matrix_width': 16,
            'timezone': 'MSK',
            'city_id': 0
        }
    
    def _create_default_preset(self, number: int) -> dict:
        """Create default preset configuration according to firmware structure."""
        return {
            'effect': 1,           # 0: effect - тип эффекта
            'fadeBright': 0,       # 1: fadeBright - использовать свою яркость (0/1)
            'bright': 255,         # 2: bright - яркость пресета
            'advMode': 1,          # 3: advMode - тип реакции (1-5)
            'soundReact': 1,       # 4: soundReact - реакция на звук (1-3)
            'min': 0,              # 5: min - мин сигнал светомузыки
            'max': 255,            # 6: max - макс сигнал светомузыки
            'speed': 128,          # 7: speed - скорость эффекта
            'palette': 1,          # 8: palette - палитра цветов
            'scale': 255,          # 9: scale - масштаб эффекта
            'fromCenter': 0,       # 10: fromCenter - эффект из центра (0/1)
            'color': 0,            # 11: color - основной цвет
            'fromPal': 0,          # 12: fromPal - использовать палитру (0=цвет, 1=палитра)
            # number НЕ входит в структуру Preset для отправки!
        }
    
    def _get_broadcast_ip(self) -> str:
        """Get broadcast IP."""
        ip = self.config["ip_address"]
        if ip.endswith("."):
            return ip + "255"
        else:
            # Если введен полный IP, берем сеть и добавляем 255
            parts = ip.split(".")
            if len(parts) == 4:
                return ".".join(parts[:3]) + ".255"
            return ip
    
    def _calculate_port(self) -> int:
        """Calculate UDP port based on current group."""
        port_num = 17
        for char in self.config["network_key"]:
            port_num *= ord(char)
            port_num %= 65536
        return (port_num % 15000) + 50000 + self._current_group
    
    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.config.get(CONF_NAME, DEFAULT_NAME),
            manufacturer="Gyver",
            model="Gyver Lamp 2"
        )
    
    @property
    def last_command(self) -> str:
        """Get last sent command."""
        return self._last_command or "No command sent"
    
    @property
    def current_preset(self) -> int:
        """Get current preset number."""
        return self._current_preset
    
    @property
    def presets(self) -> list:
        """Get list of presets."""
        return self._presets
    
    @property
    def current_preset_config(self) -> dict:
        """Get current preset configuration."""
        if 1 <= self._current_preset <= len(self._presets):
            return self._presets[self._current_preset - 1]
        return self._create_default_preset(self._current_preset)
    
    @property
    def current_group(self) -> int:
        """Get current group number."""
        return self._current_group
    
    @property
    def settings(self) -> dict:
        """Get current settings."""
        return self._settings
    
    async def update_current_preset(self, updates: dict):
        """Update current preset and send command."""
        if 1 <= self._current_preset <= len(self._presets):
            self._presets[self._current_preset - 1].update(updates)
            await self._async_save_settings()
            await self.send_presets_command(self._presets)
            self._notify_listeners()
    
    async def set_setting(self, key: str, value):
        """Update a setting value."""
        self._settings[key] = value
        await self._async_save_settings()
        self._notify_listeners()
    
    async def set_current_preset(self, preset_number: int):
        """Set current preset number and notify listeners."""
        if 1 <= preset_number <= len(self._presets):
            self._current_preset = preset_number
            await self._async_save_settings()
            self._notify_listeners()
    
    async def add_preset(self):
        """Add a new preset with current settings."""
        if len(self._presets) < 40:  # MAX_PRESETS из прошивки = 40
            # Создаем новый пресет на основе текущего
            new_preset = self.current_preset_config.copy()
            new_preset_number = len(self._presets) + 1
            
            # Добавляем новый пресет в массив
            self._presets.append(new_preset)
            
            # Переключаемся на новый пресet
            self._current_preset = new_preset_number
            
            # Сохраняем и отправляем команду
            await self._async_save_settings()
            await self.send_presets_command(self._presets)
            self._notify_listeners()
            
            _LOGGER.debug(f"Added new preset #{new_preset_number}, total presets: {len(self._presets)}")
        else:
            _LOGGER.warning("Maximum number of presets (40) reached")
    
    async def delete_last_preset(self):
        """Delete last preset."""
        if len(self._presets) > 1:
            deleted_number = len(self._presets)
            self._presets.pop()
            
            # Если удалили текущий пресет, переключаемся на предыдущий
            if self._current_preset > len(self._presets):
                self._current_preset = len(self._presets)
            
            await self._async_save_settings()
            await self.send_presets_command(self._presets)
            self._notify_listeners()
            
            _LOGGER.debug(f"Deleted preset #{deleted_number}, current preset: {self._current_preset}")
        else:
            _LOGGER.warning("Cannot delete the last preset")
    
    async def reset_presets(self):
        """Reset all presets to one default."""
        self._presets = [self._create_default_preset(1)]
        self._current_preset = 1
        await self._async_save_settings()
        await self.send_presets_command(self._presets)
        self._notify_listeners()
        
        _LOGGER.debug("Reset all presets to default")
    
    def get_preset_name(self, preset_number: int) -> str:
        """Get preset name in format Effect-Palette."""
        if 1 <= preset_number <= len(self._presets):
            preset = self._presets[preset_number - 1]
            effect_id = preset.get('effect', 1)
            palette_id = preset.get('palette', 1)
            effect_name = EFFECTS.get(effect_id, "Неизвестно")
            palette_name = PALETTES.get(palette_id, "Неизвестно")
            return f"{effect_name}-{palette_name}"
        return "Пустой"
    
    async def set_current_group(self, group_number: int):
        """Set current group and recalculate port."""
        self._current_group = group_number
        self.port = self._calculate_port()
        await self._async_save_settings()
        self._notify_listeners()
    
    def add_listener(self, listener):
        """Add listener for state changes."""
        self._listeners.append(listener)
    
    def _notify_listeners(self):
        """Notify all listeners of state changes."""
        for listener in self._listeners:
            listener()
    
    async def send_command(self, mode: int, value: int, extra_value: int = None) -> bool:
        """Send UDP command."""
        if extra_value is not None:
            cmd = f"GL,{mode},{value},{extra_value}"
        else:
            cmd = f"GL,{mode},{value}"
        
        self._last_command = cmd
        _LOGGER.debug(f"Sending command: {cmd} to {self.ip}:{self.port}")
        
        try:
            # Асинхронная отправка
            await self.hass.async_add_executor_job(
                self._send_udp_command, cmd, self.ip, self.port
            )
            
            # Обновление состояния
            if mode == 0:
                if value == 6 and extra_value is not None:  # CMD_SELECT_PRESET
                    await self.set_current_preset(extra_value)
                elif value == 4:  # CMD_PREV_PRESET
                    new_preset = self._current_preset - 1
                    if new_preset < 1:
                        new_preset = len(self._presets)
                    await self.set_current_preset(new_preset)
                elif value == 5:  # CMD_NEXT_PRESET
                    new_preset = self._current_preset + 1
                    if new_preset > len(self._presets):
                        new_preset = 1
                    await self.set_current_preset(new_preset)
            
            self._notify_listeners()
            return True
        except Exception as e:
            _LOGGER.error(f"Command failed: {e}")
            return False

    def _send_udp_command(self, cmd: str, ip: str, port: int):
        """Sync UDP send."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(cmd.encode(), (ip, port))
    
    async def send_presets_command(self, presets_data: list) -> bool:
        """Send presets configuration command according to firmware structure."""
        if not presets_data:
            return False
            
        # Build command: GL,2,<count>,<preset1_params(13)>,<preset2_params(13)>,...,<current_preset>
        cmd_parts = ["GL", '2', str(len(presets_data))]
        
        for preset in presets_data:
            # ПРАВИЛЬНЫЙ ПОРЯДОК ПАРАМЕТРОВ согласно структуре Preset (13 параметров):
            cmd_parts.extend([
                str(preset.get('effect', 1)),           # 0: effect
                str(preset.get('fadeBright', 0)),       # 1: fadeBright
                str(preset.get('bright', 255)),         # 2: bright
                str(preset.get('advMode', 1)),          # 3: advMode
                str(preset.get('soundReact', 1)),       # 4: soundReact
                str(preset.get('min', 0)),              # 5: min
                str(preset.get('max', 255)),            # 6: max
                str(preset.get('speed', 128)),          # 7: speed
                str(preset.get('palette', 1)),          # 8: palette
                str(preset.get('scale', 255)),          # 9: scale
                str(preset.get('fromCenter', 0)),       # 10: fromCenter
                str(preset.get('color', 0)),            # 11: color
                str(preset.get('fromPal', 0)),          # 12: fromPal
            ])
        
        # Добавляем текущий пресет в конец команды (как в прошивке)
        cmd_parts.append(str(self._current_preset))
        
        cmd = ','.join(cmd_parts)
        self._last_command = cmd
        
        _LOGGER.debug(f"Sending presets command: {cmd}")
        
        try:
            await self.hass.async_add_executor_job(
                self._send_udp_command, cmd, self.ip, self.port
            )
            _LOGGER.debug(f"Sent presets command for {len(presets_data)} presets")
            return True
        except Exception as e:
            _LOGGER.error(f"Presets command failed: {e}")
            return False
    
    async def send_settings_command(self, settings_data: dict) -> bool:
        """Send settings configuration command."""
        timezone_map = {"MSK": 3, "UTC": 0, "EET": 2}
        timezone_str = settings_data.get('timezone', 'MSK')
        timezone_num = timezone_map.get(timezone_str.upper(), 3)
        
        cmd_parts = [
            "GL", '1',
            str(settings_data.get('brightness', 255)),
            str(settings_data.get('adc_mode', 1)),
            str(settings_data.get('min_brightness', 0)),
            str(settings_data.get('max_brightness', 255)),
            str(settings_data.get('mode_change', 0)),
            str(settings_data.get('random_order', 0)),
            str(settings_data.get('change_period', 1)),
            str(settings_data.get('lamp_type', 1)),
            str(int(settings_data.get('max_current', 500) / 100)),
            str(settings_data.get('work_hours_from', 0)),
            str(settings_data.get('work_hours_to', 23)),
            str(settings_data.get('matrix_orientation', 1)),
            str(settings_data.get('matrix_length', 16)),
            str(settings_data.get('matrix_width', 16)),
            str(timezone_num),
            str(settings_data.get('city_id', 0))
        ]
        
        cmd = ','.join(cmd_parts)
        self._last_command = cmd
        
        try:
            await self.hass.async_add_executor_job(
                self._send_udp_command, cmd, self.ip, self.port
            )
            return True
        except Exception as e:
            _LOGGER.error(f"Settings command failed: {e}")
            return False