import sys
import os
import re
import yt_dlp
from faster_whisper import WhisperModel
import time

def clean_filename(filename):
    """Очищает имя файла от недопустимых символов."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_audio(url):
    """
    Скачивает аудиодорожку БЕЗ использования ffmpeg.
    Забирает готовый файл m4a или webm напрямую с серверов YouTube.
    """
    print(f"[*] Получение информации о видео: {url}")
    
    # Настройки для yt-dlp БЕЗ пост-процессинга ffmpeg
    ydl_opts = {
        # Ищем форматы, которые уже являются аудиофайлами (m4a или webm)
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # Важно: отключаем все, что может потребовать ffmpeg
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
            actual_filename = ydl.prepare_filename(info)
            
            # Если файл скачался (например, .webm или .m4a)
            if os.path.exists(actual_filename):
                return actual_filename, video_title
            
            # Запасной поиск файла (если имя чуть изменилось)
            base, _ = os.path.splitext(actual_filename)
            for ext in ['.m4a', '.webm', '.mp3']:
                if os.path.exists(base + ext):
                    return base + ext, video_title
                    
            return None, None
    except Exception as e:
        print(f"[!] Ошибка при скачивании аудио: {e}")
        return None, None

def transcribe_audio(audio_path, model_size="base"):
    """
    Транскрибирует аудиофайл. faster-whisper использует PyAV внутри, 
    который часто работает без системного ffmpeg.
    """
    print(f"[*] Загрузка модели Whisper ({model_size})...")
    try:
        # Используем CPU и int8 для оптимизации
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        print(f"[*] Начало транскрибации: {audio_path}")
        start_time = time.time()
        
        # segments - это генератор, транскрибация идет по ходу чтения
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        print(f"[*] Язык: '{info.language}' (вероятность {info.language_probability:.2f})")
        
        full_text = []
        for segment in segments:
            print(f"[{segment.start:05.2f}s -> {segment.end:05.2f}s] {segment.text}")
            full_text.append(segment.text)
        
        duration = time.time() - start_time
        print(f"[*] Завершено за {duration:.2f} сек.")
        
        return " ".join(full_text)
    except Exception as e:
        print(f"[!] Ошибка транскрибации: {e}")
        print("[TIP] Если ошибка связана с декодированием, возможно, файл поврежден или PyAV не справляется.")
        return None

def main():
    if len(sys.argv) < 2:
        print("Использование: python main.py \"<YOUTUBE_URL>\"")
        sys.exit(1)

    url = sys.argv[1]
    
    # 1. Скачивание
    print("\n--- Шаг 1: Скачивание (без ffmpeg) ---")
    audio_path, video_title = download_audio(url)
    
    if not audio_path or not os.path.exists(audio_path):
        print("[!] Не удалось скачать аудиофайл.")
        sys.exit(1)

    print(f"[+] Файл скачан: {audio_path}")

    try:
        # 2. Транскрибация
        print("\n--- Шаг 2: Транскрибация ---")
        text = transcribe_audio(audio_path, model_size="base")
        
        if text:
            # 3. Сохранение
            print("\n--- Шаг 3: Сохранение ---")
            safe_title = clean_filename(video_title)
            output_filename = f"{safe_title}.txt"
            
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(text)
            
            print(f"[+] Готово! Результат: {output_filename}")
        else:
            print("[!] Текст не получен.")
    
    finally:
        # Очистка
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            print(f"[*] Временный файл удален.")

if __name__ == "__main__":
    main()
