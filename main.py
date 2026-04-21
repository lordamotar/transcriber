import sys
import os
import re
import time
import yt_dlp
import questionary
from faster_whisper import WhisperModel
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, SpinnerColumn
from rich.prompt import Prompt

# Инициализируем консоль Rich
console = Console()

def clean_filename(filename):
    """Очищает имя файла от недопустимых символов."""
    if not filename:
        return f"transcription_{int(time.time())}"
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def download_audio(url, progress, task_id):
    """Скачивает аудио/видео из любого поддерживаемого источника."""
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/best[ext=mp4]/bestaudio',
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }

    try:
        progress.update(task_id, description="[bold blue]📥 Подключение и скачивание...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title') or info.get('id') or f"video_{int(time.time())}"
            actual_filename = ydl.prepare_filename(info)
            
            progress.update(task_id, advance=15)
            
            if os.path.exists(actual_filename):
                return actual_filename, video_title
                
            base, _ = os.path.splitext(actual_filename)
            for ext in ['.m4a', '.webm', '.mp3', '.mp4', '.mkv']:
                if os.path.exists(base + ext):
                    return base + ext, video_title
                    
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

def transcribe_audio(audio_path, model_size, progress, task_id):
    """Транскрибирует аудио с динамическим прогрессом."""
    try:
        progress.update(task_id, description=f"[bold magenta]⚙️ Загрузка модели '{model_size}'...")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        progress.update(task_id, advance=10)

        progress.update(task_id, description="[bold cyan]📝 Транскрибация...")
        
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        total_duration = info.duration
        full_text = []
        
        start_points = progress.tasks[task_id].completed
        
        for segment in segments:
            full_text.append(segment.text)
            
            if total_duration > 0:
                sub_progress = (segment.end / total_duration) * 75
                current_total = start_points + sub_progress
                
                color = get_bar_color(current_total)
                progress.update(task_id, 
                                completed=current_total, 
                                description=f"[bold {color}]📝 Обработка ({int(current_total)}%)...")

        return " ".join(full_text)
    except Exception as e:
        console.print(f"[bold red]![/bold red] Ошибка транскрибации: {e}")
        return None

def main():
    console.print("[bold cyan]🌟 Universal Media Transcriber v3.0[/bold cyan]\n")

    # 1. Выбор модели через стрелочное меню
    model_choice = questionary.select(
        "Выберите качество транскрибации (модель):",
        choices=[
            questionary.Choice("Base (Сбалансировано)", value="base"),
            questionary.Choice("Tiny (Очень быстро, низкая точность)", value="tiny"),
            questionary.Choice("Small (Высокая точность, дольше)", value="small"),
        ],
        style=questionary.Style([
            ('text', 'fg:white'),
            ('pointer', 'fg:cyan bold'),
            ('highlighted', 'fg:cyan bold'),
            ('selected', 'fg:green'),
        ])
    ).ask()

    if not model_choice:
        return

    # 2. Запрос ссылки
    url = Prompt.ask("\n[bold yellow]🔗 Вставьте ссылку на видео/пост[/bold yellow]")

    if not url.startswith("http"):
        console.print("[bold red]Ошибка:[/bold red] Введите корректную ссылку.")
        return

    # Красивый прогресс-бар
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task_id = progress.add_task("[bold red]Запуск...", total=100)

        # 3. Скачивание
        audio_path, video_title = download_audio(url, progress, task_id)
        
        if not audio_path:
            return

        # 4. Транскрибация
        text = transcribe_audio(audio_path, model_choice, progress, task_id)
        
        if text:
            # 5. Сохранение
            progress.update(task_id, description="[bold green]💾 Сохранение...")
            safe_title = clean_filename(video_title)
            output_filename = f"{safe_title}.txt"
            
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(text)
                
            progress.update(task_id, completed=100, description="[bold green]✅ Готово!")
            console.print(f"\n[bold green]✨ Успех![/bold green] Текст сохранен в: [italic]{output_filename}[/italic]")
        
        # Удаление временного файла
        if audio_path and os.path.exists(audio_path):
            try:
                os.remove(audio_path)
            except:
                pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]✖ Остановлено.[/bold red]")
