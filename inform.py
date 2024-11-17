import os
import logging
import json
import time
import pwnagotchi
import pwnagotchi.plugins as plugins
import pwnagotchi.ui.fonts as fonts
from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
from datetime import datetime


MULTIPLIER_ASSOCIATION = 1
MULTIPLIER_DEAUTH = 2
MULTIPLIER_HANDSHAKE = 3
MULTIPLIER_AI_BEST_REWARD = 5
JSON_KEY_LEVEL = "level"
JSON_KEY_XP = "xp"
JSON_KEY_TOTAL_XP = "total_xp"

class LevelManager:
    def __init__(self, level=1, xp=0):
        self.level = level
        self.xp = xp
        self._xp_cache = {}

    def add_xp(self, points):
        self.xp += points
        self.check_level_up()

    def check_level_up(self):
        while self.xp >= self.xp_needed():
            self.level += 1
            self.xp -= self.xp_needed()
            self._xp_cache = {}

    def xp_needed(self):
        if self.level not in self._xp_cache:
            self._xp_cache[self.level] = int(100 * (1.5 ** (self.level - 1)))
        return self._xp_cache[self.level]

    def progress_status(self, mode="progress", bar_length=10, filled_char="|", empty_char="."):
        next_level_xp = self.xp_needed()
        if mode == "progress":
            return f"{self.xp}/{next_level_xp}"
        elif mode == "custom":
            filled_length = int((self.xp / next_level_xp) * bar_length)
            bar = filled_char * filled_length + empty_char * (bar_length - filled_length)
            return f"[{bar}]"

class XPManager:
    def __init__(self, config):
        self.percent = 0
        self.calculate_initial_xp = False
        self.xp = 0
        self.level = 1
        self.total_xp = 0

        self.import_enabled = config.get("experience_import_enabled", False)
        self.import_path = config.get("experience_import_path", None)
        self.save_file = "/etc/pwnagotchi/custom-plugins/inform.json"

        if self.import_enabled and self.import_path and os.path.exists(self.import_path):
            self.import_from_config()
        elif not os.path.exists(self.save_file):
            self.save()
        else:
            try:
                self.load()
            except Exception as e:
                logging.error(f"Ошибка загрузки данных XP: {e}")
                self.calculate_initial_xp = True

        if self.level == 1 and self.xp == 0:
            self.calculate_initial_xp = True
        if self.total_xp == 0:
            self.total_xp = self.calculate_total_xp(self.level, self.xp)
            self.save()
        self.xp_required = self.calculate_xp_required(self.level)

    def import_from_config(self):

        try:
            with open(self.import_path, 'r') as f:
                config_data = json.load(f)
                
                imported_level = config_data.get("level", self.level)
                imported_xp = config_data.get("exp", self.xp)
                imported_total_xp = config_data.get("exp_tot", self.total_xp)

                self.level = imported_level
                self.xp = imported_xp
                self.total_xp = imported_total_xp

                logging.info(f"Импортировано: level={self.level}, xp={self.xp}, total_xp={self.total_xp}")
                
                self.save()
                
                self.disable_import()
        except json.JSONDecodeError:
            logging.error("Ошибка при чтении файла импорта. Проверьте формат JSON.")
            self.calculate_initial_xp = True

    def disable_import(self):
        config_path = "/etc/pwnagotchi/config.toml"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    lines = f.readlines()
                with open(config_path, 'w') as f:
                    for line in lines:
                        if "experience_import_enabled" in line:
                            f.write("main.plugins.inform.experience_import_enabled = false\n")
                        else:
                            f.write(line)
                logging.info("Импорт отключен в config.toml")
            except Exception as e:
                logging.error(f"Не удалось обновить config.toml: {e}")

    def save(self):
        data = {
            JSON_KEY_LEVEL: self.level,
            JSON_KEY_XP: self.xp,
            JSON_KEY_TOTAL_XP: self.total_xp
        }
        try:
            with open(self.save_file, 'w') as f:
                f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
                logging.info(f"Данные успешно сохранены в {self.save_file}: {data}")
        except IOError as e:
            logging.error(f"Ошибка при сохранении файла: {e}")

    def load(self):
        try:
            with open(self.save_file, 'r') as f:
                data = json.loads(f.read())
                self.level = data[JSON_KEY_LEVEL]
                self.xp = data[JSON_KEY_XP]
                self.total_xp = data[JSON_KEY_TOTAL_XP]
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Ошибка при загрузке данных XP: {e}")
            self.calculate_initial_xp = True

    def calculate_xp_required(self, level):
        if level == 1:
            return 5
        return int((level ** 3) / 2)

    def check_xp(self, agent):
        if self.xp >= self.xp_required:
            self.xp = 1
            self.level += 1
            self.xp_required = self.calculate_xp_required(self.level)
            self.show_level_up(agent)

    def calculate_total_xp(self, level, xp):
        lvl_counter = 1
        xp_sum = xp
        while lvl_counter < level:
            xp_sum += self.calculate_xp_required(lvl_counter)
            lvl_counter += 1
        return xp_sum

    def show_level_up(self, agent):
        view = agent.view()
        view.set('face', agent.ui.faces.cool)
        view.set('status', "Уровень повышен!")
        view.update(force=True)

    def add_xp_event(self, agent, xp_gain):
        self.xp += xp_gain
        self.total_xp += xp_gain
        self.check_xp(agent)
        self.save()

class Inform(plugins.Plugin):
    __author__ = '@eorstane (telegram)'
    __version__ = '1.6.9'
    __license__ = 'MIT'
    __description__ = 'Плагин для отображения возраста и статистики опыта и уровня.'

    def __init__(self):
        self.config = pwnagotchi.config.get('main', {}).get('plugins', {}).get('inform', {})
        logging.info("Config loaded for Inform plugin: " + str(self.config))
        self.config_file = self.config.get("experience_config_file", "/etc/pwnagotchi/custom-plugins/inform.json")
        self.read_file = "/root/brain.json"
        self.birth_date = self.get_birth_date_from_config()
        self.total_epochs = 0
        self.training_epochs = 0
        self.refresh_interval = self.config.get("update_interval", 5)
        self.last_refresh = time.time()
        self.epochs_training_manager = LevelManager()
        self.xp_manager = XPManager(config=self.config)
        self.xp_mode = self.config.get("experience_mode", "epochs_training")
        self.load_data(self.read_file)
        self.main_display_items = self.config.get("display_main", [1, 2, 5])
        self.secondary_display_items = self.config.get("display_secondary", [3, 4, 6])
        self.xp_display_mode = self.config.get("experience_display", "progress")
        self.custom_bar_length = self.config.get("custom_bar_length", 10)
        self.custom_filled_char = self.config.get("custom_filled_char", "|")
        self.custom_empty_char = self.config.get("custom_empty_char", ".")
        self.attribute_map = {
            1: ("Эпоха", lambda: self.format_number(self.total_epochs)),
            2: ("Тренировок", lambda: self.format_number(self.training_epochs)),
            3: ("Родился", lambda: self.birth_date),
            4: ("Прожито", self.days_lived),
            5: ("Уровень", self.get_current_level),
            6: ("Опыт", self.get_current_xp)
        }
        self.main_index = 0
        self.secondary_index = 0

    def get_birth_date_from_config(self):
        birth_date_str = self.config.get('birth_date', '')
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError:
                birth_date = 'Некорректно'
        else:
            birth_date = self.load_birth_date_from_brain()
        return birth_date or "Неизвестно"

    def load_birth_date_from_brain(self):
        try:
            with open(self.read_file) as f:
                data = json.load(f)
                if 'born_at' in data:
                    return datetime.fromtimestamp(data['born_at']).strftime('%Y-%m-%d')
        except (json.JSONDecodeError, FileNotFoundError):
            logging.warning("Не удалось загрузить дату рождения из brain.json")
        return None

    def get_current_level(self):
        if self.xp_mode == "epochs_training":
            return self.epochs_training_manager.level
        elif self.xp_mode == "exp":
            return self.xp_manager.level

    def get_current_xp(self):
        if self.xp_mode == "epochs_training":
            return self.epochs_training_manager.progress_status(
                self.xp_display_mode, 
                self.custom_bar_length, 
                self.custom_filled_char, 
                self.custom_empty_char
            )
        elif self.xp_mode == "exp":
            if self.xp_display_mode == "custom":
                filled_length = int((self.xp_manager.xp / self.xp_manager.xp_required) * self.custom_bar_length)
                bar = self.custom_filled_char * filled_length + self.custom_empty_char * (self.custom_bar_length - filled_length)
                return f"[{bar}]"
            else:
                return f"{self.xp_manager.xp}/{self.xp_manager.xp_required}"

    def on_ui_setup(self, ui):
        font = getattr(fonts, self.config.get("stats_font", "Small"), fonts.Small)
        pos = (self.config.get("stats_position_x", 60), self.config.get("stats_position_y", 85))
        ui.add_element('MainStats', LabeledValue(color=BLACK, label='', value='', position=pos, label_font=font, text_font=font))
        add_font = getattr(fonts, self.config.get("additional_stats_font", "Small"), fonts.Small)
        add_pos = (self.config.get("additional_stats_position_x", 60), self.config.get("additional_stats_position_y", 95))
        ui.add_element('SecondaryStats', LabeledValue(color=BLACK, label='', value='', position=add_pos, label_font=add_font, text_font=add_font))

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('MainStats')
            ui.remove_element('SecondaryStats')

    def update_main_display(self, ui):
        item = self.main_display_items[self.main_index]
        if item in self.attribute_map:
            label, value_fn = self.attribute_map[item]
            ui.set('MainStats', f"{label}: {value_fn()}")
        self.main_index = (self.main_index + 1) % len(self.main_display_items)

    def update_secondary_display(self, ui):
        item = self.secondary_display_items[self.secondary_index]
        if item in self.attribute_map:
            label, value_fn = self.attribute_map[item]
            ui.set('SecondaryStats', f"{label}: {value_fn()}")
        self.secondary_index = (self.secondary_index + 1) % len(self.secondary_display_items)

    def on_ui_update(self, ui):
        if time.time() - self.last_refresh >= self.refresh_interval:
            self.last_refresh = time.time()
            self.update_main_display(ui)
            self.update_secondary_display(ui)
            ui.update(force=True)

    def on_ai_training_step(self, agent, _locals, _globals):
        if self.xp_mode == "epochs_training":
            self.training_epochs += 1
            self.epochs_training_manager.add_xp(10)

    def on_epoch(self, agent, epoch, epoch_data):
        if self.xp_mode == "epochs_training":
            self.total_epochs += 1
            self.epochs_training_manager.add_xp(5)

    def on_association(self, agent, access_point):
        if self.xp_mode == "exp":
            self.xp_manager.add_xp_event(agent, MULTIPLIER_ASSOCIATION)

    def on_deauthentication(self, agent, access_point, client_station):
        if self.xp_mode == "exp":
            self.xp_manager.add_xp_event(agent, MULTIPLIER_DEAUTH)

    def on_handshake(self, agent, filename, access_point, client_station):
        if self.xp_mode == "exp":
            self.xp_manager.add_xp_event(agent, MULTIPLIER_HANDSHAKE)

    def on_ai_best_reward(self, agent, reward):
        if self.xp_mode == "exp":
            self.xp_manager.add_xp_event(agent, MULTIPLIER_AI_BEST_REWARD)

    def format_number(self, number):
        if abs(number) < 1000:
            return str(number)
        elif abs(number) < 1_000_000:
            return f"{number / 1000:.1f}K"
        elif abs(number) < 1_000_000_000:
            return f"{number / 1_000_000:.1f}M"
        else:
            return f"{number / 1_000_000_000:.1f}B"

    def days_lived(self):
        if self.birth_date not in ["Неизвестно", "Некорректно"]:
            try:
                birth_date_str = self.birth_date.rstrip('*')
                birth_date_obj = datetime.strptime(birth_date_str, '%Y-%m-%d')
                return f"{(datetime.now() - birth_date_obj).days} дней"
            except ValueError:
                pass
        return "Неизвестно"

    def load_data(self, file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    self.total_epochs = data.get('epochs_lived', 0)
                    self.training_epochs = data.get('epochs_trained', 0)
                    level, xp = data.get('level', 1), data.get('xp', 0)
                    self.epochs_training_manager = LevelManager(level=level, xp=xp)
                    if level == 1 and xp == 0:
                        self.calculate_initial_level()
                    if self.birth_date is None:
                        self.birth_date = datetime.fromtimestamp(data.get('born_at', 0)).strftime('%Y-%m-%d') if data.get('born_at') else "Неизвестно"
            except json.JSONDecodeError:
                logging.warning("Ошибка при загрузке данных из файла")

    def calculate_initial_level(self):
        total_xp = self.total_epochs * 5 + self.training_epochs * 10
        self.epochs_training_manager = LevelManager()
        self.epochs_training_manager.add_xp(total_xp)
