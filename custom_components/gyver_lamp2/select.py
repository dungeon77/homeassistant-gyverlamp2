"""Select platform for Gyver Lamp 2."""
from __future__ import annotations
import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MODE_CONTROL, CMD_SELECT_PRESET, ADC_MODES, CHANGE_PERIODS, LAMP_TYPES, EFFECTS, PALETTES, REACTION_TYPES, SOUND_REACTIONS
from .device import GyverLamp2Device

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    device = hass.data[DOMAIN][entry.entry_id]
    
    selects = [
        # Control (None category)
        GyverLamp2PresetSelect(device),
        GyverLamp2GroupSelect(device),
        
        # Settings (Type 1)
        GyverLamp2SettingsSelect(device, "ADC Mode", "adc_mode", ADC_MODES, 
                                ADC_MODES.get(device.settings.get('adc_mode', 1), "Выкл"), 
                                "mdi:audio-input-rca", "settings", EntityCategory.CONFIG),
        GyverLamp2SettingsSelect(device, "Mode Change", "mode_change", {0: "Ручная", 1: "Авто"}, 
                                "Ручная" if device.settings.get('mode_change', 0) == 0 else "Авто", 
                                "mdi:auto-mode", "settings", EntityCategory.CONFIG),
        GyverLamp2SettingsSelect(device, "Lamp Type", "lamp_type", LAMP_TYPES, 
                                LAMP_TYPES.get(device.settings.get('lamp_type', 1), "Лента"), 
                                "mdi:led-strip", "settings", EntityCategory.CONFIG),
        GyverLamp2SettingsSelect(device, "Matrix Orientation", "matrix_orientation", 
                                {i: f"Ориентация {i}" for i in range(1, 9)}, 
                                f"Ориентация {device.settings.get('matrix_orientation', 1)}", 
                                "mdi:arrow-all", "settings", EntityCategory.CONFIG),
        GyverLamp2SettingsSelect(device, "Change Period", "change_period", CHANGE_PERIODS, 
                                CHANGE_PERIODS.get(device.settings.get('change_period', 1), "1 мин"), 
                                "mdi:timer", "settings", EntityCategory.CONFIG),
        
        # Preset Settings (Type 2)
        GyverLamp2SettingsSelect(device, "Preset Effect", "preset_effect", EFFECTS, 
                                EFFECTS.get(device.current_preset_config.get('effect', 1), "Перлин"), 
                                "mdi:star-four-points", "preset", EntityCategory.CONFIG),
        GyverLamp2SettingsSelect(device, "Preset Palette", "preset_palette", PALETTES, 
                                PALETTES.get(device.current_preset_config.get('palette', 1), "Кастом"), 
                                "mdi:palette-swatch", "preset", EntityCategory.CONFIG),
        GyverLamp2SettingsSelect(device, "Preset Reaction", "preset_reaction", REACTION_TYPES, 
                                REACTION_TYPES.get(device.current_preset_config.get('advMode', 1), "Нет"), 
                                "mdi:plus-box", "preset", EntityCategory.CONFIG),
        GyverLamp2SettingsSelect(device, "Preset Sound Reaction", "preset_sound_reaction", SOUND_REACTIONS, 
                                SOUND_REACTIONS.get(device.current_preset_config.get('soundReact', 1), "Яркость"), 
                                "mdi:music-note", "preset", EntityCategory.CONFIG),
    ]
    async_add_entities(selects)

class GyverLamp2PresetSelect(SelectEntity):
    """Select for preset selection."""
    
    def __init__(self, device: GyverLamp2Device):
        """Initialize the select."""
        self._device = device
        self._attr_name = "Preset"
        self._attr_unique_id = f"{device.entry.entry_id}_preset_select"
        self._attr_device_info = device.device_info
        self._attr_icon = "mdi:palette"
        self._attr_entity_category = None
        self._attr_has_entity_name = True
        self._update_options()
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        self._update_options()
        self.async_write_ha_state()
    
    def _update_options(self):
        """Update preset options."""
        self._attr_options = []
        for i in range(1, len(self._device.presets) + 1):
            preset_name = self._device.get_preset_name(i)
            self._attr_options.append(f"{i}. {preset_name}")
        
        if self._attr_options and 1 <= self._device.current_preset <= len(self._attr_options):
            self._attr_current_option = self._attr_options[self._device.current_preset - 1]
        else:
            self._attr_current_option = None
    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            preset_number = int(option.split('.')[0])
            await self._device.send_command(MODE_CONTROL, CMD_SELECT_PRESET, preset_number)
        except (ValueError, IndexError):
            _LOGGER.error(f"Invalid preset option: {option}")

class GyverLamp2GroupSelect(SelectEntity):
    """Select for group selection."""
    
    def __init__(self, device: GyverLamp2Device):
        """Initialize the group select."""
        self._device = device
        self._attr_name = "Group"
        self._attr_unique_id = f"{device.entry.entry_id}_group_select"
        self._attr_device_info = device.device_info
        self._attr_icon = "mdi:account-group"
        self._attr_entity_category = None
        self._attr_has_entity_name = True
        self._attr_options = [f"Группа {i}" for i in range(1, 9)]
        self._attr_current_option = self._attr_options[self._device.current_group - 1]
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        self._attr_current_option = self._attr_options[self._device.current_group - 1]
        self.async_write_ha_state()
    
    async def async_select_option(self, option: str) -> None:
        """Change the selected group."""
        group_number = self._attr_options.index(option) + 1
        await self._device.set_current_group(group_number)
        self.async_write_ha_state()

class GyverLamp2SettingsSelect(SelectEntity):
    """Select for device settings."""
    
    def __init__(self, device: GyverLamp2Device, name: str, unique_id_suffix: str, options: dict, default_option: str, icon: str, setting_type: str, entity_category: EntityCategory):
        """Initialize settings select."""
        self._device = device
        self._attr_name = name
        self._attr_unique_id = f"{device.entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = device.device_info
        self._attr_options = list(options.values())
        self._attr_current_option = default_option
        self._attr_icon = icon
        self._attr_entity_category = entity_category
        self._attr_has_entity_name = True
        self._options_dict = options
        self._setting_key = unique_id_suffix
        self._setting_type = setting_type
        
        # Маппинг для пресетов (ИСПРАВЛЕНО)
        self._key_mapping = {
            'preset_effect': 'effect',
            'preset_palette': 'palette', 
            'preset_reaction': 'advMode',
            'preset_sound_reaction': 'soundReact'
        }
        
        device.add_listener(self._handle_device_update)
    
    def _handle_device_update(self):
        """Handle device state updates."""
        if self._setting_type == "settings":
            current_value = self._device.settings.get(self._setting_key, 0)
        elif self._setting_type == "preset":
            # Используем маппинг для пресетов
            preset_key = self._key_mapping.get(self._setting_key, self._setting_key.replace('preset_', ''))
            current_value = self._device.current_preset_config.get(preset_key, 0)
        
        self._attr_current_option = self._options_dict.get(current_value, self._attr_options[0])
        self.async_write_ha_state()
    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        for key, value in self._options_dict.items():
            if value == option:
                if self._setting_type == "settings":
                    await self._device.set_setting(self._setting_key, key)
                elif self._setting_type == "preset":
                    # Используем маппинг для пресетов
                    preset_key = self._key_mapping.get(self._setting_key, self._setting_key.replace('preset_', ''))
                    await self._device.update_current_preset({preset_key: key})
                break
        self.async_write_ha_state()