# Diablo 4 Overlay — World Boss & Helltide

Компактный оверлей поверх игры который показывает таймер до следующего **World Boss** и статус **Helltide** в реальном времени.

Данные берутся с [helltides.com](https://helltides.com) — самого популярного трекера событий D4.

---

## Скриншот

![overlay preview](preview.png)

---

## Установка (первый раз)

> Требуется **Python 3.8+** — [скачать тут](https://www.python.org/downloads/)  
> При установке Python поставьте галочку **"Add Python to PATH"**

**1.** Скачайте архив: **[Releases →](https://github.com/uh616/d4-world-boss-overlay/releases/latest)**  
**2.** Распакуйте куда удобно  
**3.** Запустите `install.bat` — он поставит необходимые зависимости (один раз)  
**4.** Запускайте `start_overlay.bat` каждый раз перед игрой

---

## Использование

| Действие | Как |
|---|---|
| Перетащить оверлей | Зажать ЛКМ и тащить |
| Закрыть оверлей | Нажать **✕** справа |

---

## Кастомный звук (5 минут до World Boss)

По умолчанию играет стандартный звук Windows.

**Чтобы поставить свой звук:**
1. Найдите любой `.wav` файл (MP3 не подходит, конвертируйте через [CloudConvert](https://cloudconvert.com/mp3-to-wav))
2. Положите его в папку рядом с `overlay.py`
3. Переименуйте в **`alert.wav`**

**Чтобы убрать звук совсем:**  
Просто не кладите файл `alert.wav` — будет стандартный Windows-звук. Или закомментируйте строку `_play_sound` в коде.

---

## Для разработчиков

```bash
git clone https://github.com/uh616/d4-world-boss-overlay.git
cd d4-world-boss-overlay
pip install -r requirements.txt
python overlay.py
```

---

## Данные

Таймер использует неофициальный API сайта **helltides.com**. Если сайт недоступен — оверлей покажет "connecting..." и попробует снова через 5 минут.

---

*Сделано для зрителей [Twitch канала uh616](https://www.twitch.tv/uh616)*
