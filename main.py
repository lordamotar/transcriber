import sys
import os
import re
import time
import yt_dlp
from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
from rich.prompt import Prompt

# Инициализируем консоль Rich для красивого вывода
console = Console()

def clean_filename(filename):
    """Очищает имя файла от недопустимых символов."""
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_audio(url, progress, task_id):
    """Скачивает аудио и обновляет прогресс-бар (этап скачивания - первые 15%)."""
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        progress.update(task_id, description="[bold blue]📥 Скачивание аудио...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title', 'video')
            actual_filename = ydl.prepare_filename(info)
            
            # Немного продвигаем прогресс после скачивания
            progress.update(task_id, advance=15)
            
            if os.path.exists(actual_filename):
                return actual_filename, video_title
            return None, None
    except Exception as e:
        console.print(f"[bold red]![/bold red] Ошибка при скачивании: {e}")
        return None, None

def get_bar_color(percentage):
    """Возвращает цвет в зависимости от процента выполнения."""
    if percentage < 25:
        return "red"
    elif percentage < 50:
        return "orange3"
    elif percentage < 75:
        return "yellow"
    else:
        return "green"

def transcribe_audio(audio_path, progress, task_id):
    """Транскрибирует аудио с динамическим обновлением прогресс-бара."""
    try:
        progress.update(task_id, description="[bold magenta]⚙️ Загрузка модели...")
        # Инициализация модели (занимает время)
        model = WhisperModel("base", device="cpu", compute_type="int8")
        progress.update(task_id, advance=10) # +10% за загрузку модели

        progress.update(task_id, description="[bold cyan]📝 Транскрибация...")
        
        # Получаем сегменты
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        total_duration = info.duration
        full_text = []
        
        # Прогресс транскрибации занимает оставшиеся 75% (от 25 до 100)
        start_points = progress.tasks[task_id].completed
        
        for segment in segments:
            full_text.append(segment.text)
            
            # Вычисляем процент на основе текущего времени сегмента
            if total_duration > 0:
                # Сколько % от транскрибации пройдено
                sub_progress = (segment.end / total_duration) * 75
                current_total = start_points + sub_progress
                
                # Обновляем цвет и значение
                color = get_bar_color(current_total)
                progress.update(task_id, 
                                completed=current_total, 
                                description=f"[bold {color}]📝 Транскрибация ({int(current_total)}%)...")

        return " ".join(full_text)
    except Exception as e:
        console.print(f"[bold red]![/bold red] Ошибка транскрибации: {e}")
        return None

def main():
    console.print("[bold cyan]🚀 YouTube Transcriber v2.0[/bold cyan]\n")

    # 1. Запрос ссылки (интерактивно, если нет в аргументах)
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = Prompt.ask("[bold yellow]🔗 Вставьте ссылку на YouTube видео[/bold yellow]")

    if not url.startswith("http"):
        console.print("[bold red]Ошибка:[/bold red] Введите корректную ссылку.")
        return

    # Создаем красивый прогресс-бар
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task_id = progress.add_task("[bold red]Подготовка...", total=100)

        # 2. Скачивание
        audio_path, video_title = download_audio(url, progress, task_id)
        
        if not audio_path:
            return

        # 3. Транскрибация
        text = transcribe_audio(audio_path, progress, task_id)
        
        if text:
            # 4. Сохранение
            progress.update(task_id, description="[bold green]💾 Сохранение...")
            safe_title = clean_filename(video_title)
            output_filename = f"{safe_title}.txt"
            
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(text)
                
            progress.update(task_id, completed=100, description="[bold green]✅ Готово!")
            
            console.print(f"\n[bold green]✨ Успех![/bold green] Текст сохранен в: [italic]{output_filename}[/italic]")
        
        # Удаляем временный файл
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]✖ Работа остановлена пользователем.[/bold red]")
