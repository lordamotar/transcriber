# YouTube Transcriber 🎥 -> 📝

[RU] Автоматическая транскрибация YouTube-видео в текст с использованием локальной модели Whisper и красивым интерфейсом.  
[EN] Automatic YouTube video transcription to text using a local Whisper model with a beautiful UI.

---

## 🇷🇺 Русский (RU)

### Особенности
- **Интерактивность**: Просто запустите скрипт, и он сам спросит ссылку.
- **Цветной Прогресс-бар**: Динамическая индикация (Красный 🔴 -> Оранжевый 🟠 -> Желтый 🟡 -> Зеленый 🟢).
- **Без внешних зависимостей**: Работает без `ffmpeg` в системе.
- **Приватность**: Все вычисления происходят локально.

### Использование
1. Установите зависимости: `uv sync`
2. Запустите: `uv run python main.py`

---

## 🇺🇸 English (EN)

### Features
- **Interactive**: Just run the script, and it will prompt you for the URL.
- **Colored Progress Bar**: Dynamic completion states (Red 🔴 -> Orange 🟠 -> Yellow 🟡 -> Green 🟢).
- **No System dependencies**: Works without system-wide `ffmpeg`.
- **Privacy**: All computations are handled locally.

### Usage
1. Install dependencies: `uv sync`
2. Run: `uv run python main.py`

---

## ☕ Поддержка / Support

Если вам помог этот инструмент, вы можете выразить благодарность:  
If this tool helped you, you can show your support:

**Wallet (TON/USDT):**  
`UQC2O8SxqGZ0VRYPDnNEYd2ASHui0dZF_YIQQ1bD1xnJFy8z`

---

## 🛠️ Технологии / Built with
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [rich](https://github.com/Textualize/rich)
- [uv](https://github.com/astral-sh/uv)
