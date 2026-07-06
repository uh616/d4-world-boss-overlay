# Diablo 4 Overlay — World Boss & Helltide

Компактный оверлей поверх игры который показывает таймер до следующего **World Boss** и статус **Helltide** в реальном времени. Данные берутся с [helltides.com](https://helltides.com).

---

## ⬇️ Скачать

**[→ Releases (скачать D4-Overlay.exe)](https://github.com/uh616/d4-world-boss-overlay/releases/latest)**

Никакого Python не нужно — просто скачай и запусти!

---

## Установка

1. Скачайте **`D4-Overlay.exe`** из последнего [Release](https://github.com/uh616/d4-world-boss-overlay/releases/latest)
2. Положите файл куда удобно (например, рабочий стол)
3. Запустите — оверлей появится в верхнем левом углу экрана

> ⚠️ Windows Defender может показать предупреждение "Неизвестный издатель" — это нормально для неподписанных программ. Нажмите **"Подробнее" → "Всё равно запустить"**.

---

## Использование

| Действие | Как |
|---|---|
| Перетащить оверлей | Зажать ЛКМ и тащить |
| Закрыть оверлей | Нажать **✕** справа |

---

## Что показывает

```
Ashava & Avarice  01:23:45  ║  HT: 38:21  🖼  ✕
```

- **Слева** — имя World Boss и обратный отсчёт до появления
- **HT: XX:XX** — оставшееся время активного Helltide (красный)
- **HT in XX:XX** — время до начала следующего Helltide (серый)
- **⚔ World Boss Active!** — когда босс уже появился

---

## Кастомный звук (сигнал за 5 минут до World Boss)

По умолчанию играет стандартный звук Windows.

**Чтобы поставить свой звук:**
1. Найдите `.wav` файл (MP3 → конвертируй на [CloudConvert](https://cloudconvert.com/mp3-to-wav))
2. Положи рядом с `D4-Overlay.exe`
3. Переименуй в **`alert.wav`**

**Чтобы вернуть стандартный звук** — просто удали `alert.wav`.

---

## Для разработчиков (запуск из исходников)

```bash
git clone https://github.com/uh616/d4-world-boss-overlay.git
cd d4-world-boss-overlay
pip install -r requirements.txt
python overlay.py
```

**Собрать .exe:**
```bash
python build.py
```

---

*Сделано для зрителей [Twitch канала solnechniyre6enok](https://www.twitch.tv/solnechniyre6enok)*
