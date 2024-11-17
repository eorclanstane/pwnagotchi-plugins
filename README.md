# Плагин Inform для Pwnagotchi

**Inform** — это плагин для Pwnagotchi, который отслеживает возраст устройства, прогресс обучения ИИ, статистику опыта и уровня. Плагин позволяет продолжить прогресс с сохраненного уровня благодаря возможности импорта данных из других конфигураций. Он динамически обновляет отображаемую информацию, чередуя выбранные элементы интерфейса.

![Демонстрация](https://raw.githubusercontent.com/eorclanstane/pwnagotchi-plugins/main/inform.gif)                                            

---

## Основные возможности:
- **Режимы опыта**:
  - Поддержка двух режимов начисления опыта:
    - `epochs_training`: опыт начисляется за количество эпох и тренировок ИИ.
    - `exp`: опыт начисляется за действия, такие как ассоциации, деаутентификации, захват хендшейков и лучшие награды ИИ.

- **Отслеживание уровня и прогресса**:
  - Уровни повышаются по мере накопления опыта, а количество необходимого XP увеличивается с каждым новым уровнем.
  - Возможность выбора режима отображения прогресса:
    - `progress`: текущий опыт и требуемое количество для следующего уровня.
    - `custom`: визуальный прогресс-бар с настраиваемой длиной и символами.

- **Динамическое обновление элементов интерфейса**:
  - Плагин автоматически переключает отображаемую информацию, например:
    - Текущее количество эпох.
    - Количество тренировок.
    - Уровень и текущий опыт.
    - Возраст устройства.
  - Настройка шрифтов, положения элементов и списка отображаемых параметров.

- **Импорт и экспорт данных**:
  - Импорт сохраненных данных из других плагинов или JSON-файлов для продолжения с существующего уровня.
  - Экспорт текущего уровня, опыта и статистики в JSON для последующего использования.

- **Уведомления о повышении уровня**:
  - При достижении нового уровня на экране отображается уведомление, а "эмоция" устройства изменяется.

| **Переменная**                                    | **Описание**                                                                                | **Значение по умолчанию / Пример**           |
|---------------------------------------------------|---------------------------------------------------------------------------------------------|----------------------------------------------|
| `main.plugins.inform.enabled`                     | Включает или отключает плагин.                                                              | `true`                                       |
| `main.plugins.inform.experience_import_enabled`   | Включает импорт опыта из указанного файла.                                                  | `false`                                      |
| `main.plugins.inform.experience_import_path`      | Путь к файлу для импорта опыта.                                                             | `/etc/pwnagotchi/update.json`                |
| `main.plugins.inform.experience_config_file`      | Путь к файлу для сохранения данных опыта.                                                   | `/etc/pwnagotchi/inform.json`                |
| `main.plugins.inform.birth_date`                  | Дата рождения устройства. Если пусто, берется из `brain.json`.                              | `"2024-11-17"`                               |
| `main.plugins.inform.update_interval`             | Интервал обновления статистики (в секундах).                                                | `5`                                          |
| `main.plugins.inform.experience_mode`             | Режим опыта: `epochs_training` для тренировок или `exp` для событий.                        | `"epochs_training"`                          |
| `main.plugins.inform.display_main`                | Список атрибутов для отображения в основном элементе UI.                                    | `[1, 2, 5]`                                  |
| `main.plugins.inform.display_secondary`           | Список атрибутов для отображения в дополнительном элементе UI.                              | `[3, 4, 6]`                                  |
| `main.plugins.inform.experience_display`          | Тип отображения опыта: `progress` или `custom`.                                             | `"progress"`                                 |
| `main.plugins.inform.custom_bar_length`           | Длина пользовательской полосы прогресса (в символах).                                       | `10`                                         |
| `main.plugins.inform.custom_filled_char`          | Символ для заполненной части полосы прогресса.                                              | `"\|"`                                       |
| `main.plugins.inform.custom_empty_char`           | Символ для незаполненной части полосы прогресса.                                            | `"."`                                        |
| `main.plugins.inform.stats_font`                  | Шрифт для основного элемента UI.                                                            | `"Small"`                                    |
| `main.plugins.inform.stats_position_x`            | Координата X для основного элемента UI.                                                     | `60`                                         |
| `main.plugins.inform.stats_position_y`            | Координата Y для основного элемента UI.                                                     | `85`                                         |
| `main.plugins.inform.additional_stats_font`       | Шрифт для дополнительного элемента UI.                                                      | `"Small"`                                    |
| `main.plugins.inform.additional_stats_position_x` | Координата X для дополнительного элемента UI.                                               | `60`                                         |
| `main.plugins.inform.additional_stats_position_y` | Координата Y для дополнительного элемента UI.                                               | `95`                                         |

Плагин поддерживает настройку отображаемых атрибутов через параметры `main.plugins.inform.display_main` и `main.plugins.inform.display_secondary` в `config.toml`. Вы можете указать, какие именно метрики будут показываться в основной и дополнительной области пользовательского интерфейса, используя их номера.

### Список доступных атрибутов

| **Номер атрибута**  | **Описание**                                                                                      |
|---------------------|---------------------------------------------------------------------------------------------------|
| **1: Эпоха**        | Показывает общее количество завершенных эпох (итераций обучения Pwnagotchi).                      |
| **2: Тренировок**   | Отображает общее количество выполненных тренировочных шагов (обучение искусственного интеллекта). |
| **3: Родился**      | Дата рождения устройства. Если не указана, берется из файла `brain.json`.                         |
| **4: Прожито**      | Количество дней с момента рождения устройства.                                                    |
| **5: Уровень**      | Текущий уровень устройства, основанный на накопленном опыте.                                      |
| **6: Опыт**         | Текущий прогресс опыта до следующего уровня, в текстовом или графическом формате.                 |

### Пример конфигурации

Чтобы отобразить в основной области UI **Эпоха**, **Тренировок**, и **Уровень**, а в дополнительной области **Родился**, **Прожито**, и **Опыт**, добавьте следующее в `config.toml`:

```toml
main.plugins.inform.display_main = [1, 2, 5]
main.plugins.inform.display_secondary = [3, 4, 6]
```

   ## Установка
1. Скопируйте файл `inform.py` в папку `/etc/pwnagotchi/custom-plugins/`:
   ```bash
   sudo cp inform.py /etc/pwnagotchi/custom-plugins/
2. Добавьте следующие строки в файл config.toml для запуска плагина:

```toml
main.plugins.inform.enabled = true
main.plugins.inform.experience_mode = "epochs_training"
main.plugins.inform.update_interval = 5
main.plugins.inform.birth_date = "2024-11-17"
main.plugins.inform.experience_display = "progress"
main.plugins.inform.custom_bar_length = 10
main.plugins.inform.custom_filled_char = "|"
main.plugins.inform.custom_empty_char = "."
main.plugins.inform.experience_import_enabled = false
main.plugins.inform.experience_import_path = ""
main.plugins.inform.experience_config_file = "/etc/pwnagotchi/inform.json"
main.plugins.inform.display_main = [1, 2, 5]
main.plugins.inform.display_secondary = [3, 4, 6]
main.plugins.inform.stats_font = "Small"
main.plugins.inform.stats_position_x = 60
main.plugins.inform.stats_position_y = 85
main.plugins.inform.additional_stats_font = "Small"
main.plugins.inform.additional_stats_position_x = 60
main.plugins.inform.additional_stats_position_y = 95
```
Перезапустите Pwnagotchi для применения изменений:

```bash
sudo systemctl restart pwnagotchi
```

