"""Constants."""
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME

DOMAIN = "gyver_lamp2"
DEFAULT_NAME = "Gyver Lamp 2"
DEFAULT_KEY = "GL"
DEFAULT_GROUP = 1

CONF_NETWORK_KEY = "network_key"
CONF_GROUP_NUMBER = "group_number"

# UDP Protocol
MODE_CONTROL = 0
MODE_SETTINGS = 1
MODE_PRESETS = 2
CMD_OFF = 0
CMD_ON = 1
CMD_PREV_PRESET = 4
CMD_NEXT_PRESET = 5
CMD_SELECT_PRESET = 6
CMD_REBOOT = 11

# Effects (актуальные из исходников)
EFFECTS = {
    1: "Перлин",
    2: "Цвет", 
    3: "Смена цвета",
    4: "Градиент",
    5: "Частицы",
    6: "Огонь",
    7: "Огонь 2020",
    8: "Конфетти",
    9: "Смерч",
    10: "Часы",
    11: "Погода"
}

# Palettes
PALETTES = {
    1: "Кастом",
    2: "Тепловая",
    3: "Огненная", 
    4: "Лава",
    5: "Вечеринка",
    6: "Радуга",
    7: "Полосатая радуга",
    8: "Облака",
    9: "Океан",
    10: "Лес",
    11: "Закат",
    12: "Полиция",
    13: "Оптимус Прайм",
    14: "Тёплая лава",
    15: "Холодная лава",
    16: "Горячая лава",
    17: "Розовая лава",
    18: "Уютный",
    19: "Киберпанк",
    20: "Девчачая",
    21: "Рождество",
    22: "Кислота",
    23: "Синий дым",
    24: "Жвачка",
    25: "Леопард",
    26: "Аврора"
}

# Reaction types (ИСПРАВЛЕНО по прошивке)
REACTION_TYPES = {
    1: "Нет",        # GL_ADV_NONE
    2: "Громкость",  # GL_ADV_VOL
    3: "Низкие",     # GL_ADV_LOW
    4: "Высокие",    # GL_ADV_HIGH
    5: "Часы"        # GL_ADV_CLOCK
}

# Sound reactions (ИСПРАВЛЕНО по прошивке)
SOUND_REACTIONS = {
    1: "Яркость",    # GL_REACT_BRI
    2: "Масштаб",    # GL_REACT_SCL
    3: "Длина"       # GL_REACT_LEN
}

# Change periods
CHANGE_PERIODS = {
    1: "1 мин",
    5: "5 мин", 
    10: "10 мин",
    15: "15 мин",
    25: "25 мин", 
    30: "30 мин",
    40: "40 мин",
    50: "50 мин",
    60: "60 мин"
}

# ADC Modes (ИСПРАВЛЕНО по прошивке)
ADC_MODES = {
    1: "Выкл",       # GL_ADC_NONE
    2: "Яркость",    # GL_ADC_BRI
    3: "Музыка",     # GL_ADC_MIC
    4: "Оба"         # GL_ADC_BOTH
}

# Lamp types
LAMP_TYPES = {
    1: "Лента",
    2: "Зигзаг",
    3: "Спираль"
}