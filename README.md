# Universal Media Transcriber 🎥 -> 📝

[RU] Автоматическая транскрибация видео и аудио в текст. Две версии: для процессора (CPU) и видеокарты (GPU).  
[EN] Automatic transcription of video and audio to text. Two versions: for CPU and GPU.

---

## 🇷🇺 Русский (RU)

### Выбор версии
В проекте доступны два скрипта:
1.  **`transcribe_cpu.py`**: Оптимизирован для процессоров. Работает без системных зависимостей (не нужен `ffmpeg`). 
2.  **`transcribe_gpu.py`**: Оптимизирован для NVIDIA GPU (CUDA). Требует установленный `ffmpeg` и видеокарту. В 5-10 раз быстрее.

### Установка
```bash
uv sync
```

### Запуск
- Для процессора: `uv run python transcribe_cpu.py`
- Для видеокарты: `uv run python transcribe_gpu.py`

---

## 🇺🇸 English (EN)

### Choose Your Version
Two scripts are available:
1.  **`transcribe_cpu.py`**: Optimized for CPUs. Self-contained (no `ffmpeg` required).
2.  **`transcribe_gpu.py`**: Optimized for NVIDIA GPUs (CUDA). Requires `ffmpeg` and a GPU. 5-10x faster.

### Installation
```bash
uv sync
```

### Usage
- For CPU: `uv run python transcribe_cpu.py`
- For GPU: `uv run python transcribe_gpu.py`

---

## ☕ Поддержка / Support
**Wallet (TON/USDT):**  
`UQC2O8SxqGZ0VRYPDnNEYd2ASHui0dZF_YIQQ1bD1xnJFy8z`

---

## 🛠️ Технологии / Built with
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- [rich](https://github.com/Textualize/rich)
- [questionary](https://github.com/tmbo/questionary)
