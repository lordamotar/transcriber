# YouTube Transcriber 🎥 -> 📝

[RU] Автоматическая транскрибация YouTube-видео в текст с использованием локальной модели Whisper.  
[EN] Automatic YouTube video transcription to text using a local Whisper model.

---

## 🇷🇺 Русский (RU)

### Особенности
- **Без внешних зависимостей**: Работает без установки `ffmpeg` в систему (использует встроенный декодер).
- **Производительность**: Оптимизировано через `faster-whisper` для работы на CPU.
- **Приватность**: Все вычисления происходят локально.

### Установка
Рекомендуется использовать [uv](https://github.com/astral-sh/uv):
```bash
uv sync
```

### Использование
```bash
uv run python main.py "URL_ВИДЕО"
```

---

## 🇺🇸 English (EN)

### Features
- **No System dependencies**: Works without system-wide `ffmpeg` installation (uses built-in decoder).
- **Performance**: Optimized via `faster-whisper` for efficient CPU usage.
- **Privacy**: All computations are handled locally.

### Installation
Using [uv](https://github.com/astral-sh/uv) is recommended:
```bash
uv sync
```

### Usage
```bash
uv run python main.py "VIDEO_URL"
```

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
- [uv](https://github.com/astral-sh/uv)
