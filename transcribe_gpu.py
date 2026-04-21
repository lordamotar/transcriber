import sys
import os
import re
import time
import yt_dlp
import questionary
import torch
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

def check_cuda():
    """Проверяет доступность NVIDIA GPU."""
    if not torch.cuda.is_available():
        console.print("[bold red]ВНИМАНИЕ:[/bold red] NVIDIA GPU не обнаружен. Скрипт может упасть или работать на CPU.")
        return False
    console.print(f"[bold green]GPU обнаружен:[/bold green] {torch.cuda.get_device_name(0)}")
    return True

def download_audio(url, progress, task_id):
    """Скачивает аудио высокого качества с использованием ffmpeg."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
        'outtmpl': '%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }

    try:
        progress.update(task_id, description="[bold blue]📥 Скачивание аудио (High Quality)...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title') or info.get('id') or f"video_{int(time.time())}"
            # Учитываем, что после ffmpeg расширение будет m4a
            temp_filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(temp_filename)
            actual_filename = base + ".m4a"
            
            progress.update(task_id, advance=15)
            
            if os.path.exists(actual_filename):
                return actual_filename, video_title
            return None, None
    except Exception as e:
        console.print(f"[bold red]![/bold red] Ошибка скачивания (проверьте, установлен ли ffmpeg): {e}")
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
    """Транскрибирует аудио на GPU с использованием CUDA."""
    try:
        progress.update(task_id, description=f"[bold magenta]⚙️ Загрузка модели '{model_size}' на GPU...")
        # device="cuda" и float16 - оптимально для видеокарт
        model = WhisperModel(model_size, device="cuda", compute_type="float16")
        progress.update(task_id, advance=10)

        progress.update(task_id, description="[bold cyan]⚡ GPU Транскрибация...")
        
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
                                description=f"[bold {color}]⚡ Обработка ({int(current_total)}%)...")

        return " ".join(full_text)
    except Exception as e:
        console.print(f"[bold red]![/bold red] Ошибка GPU транскрибации: {e}")
        console.print("[TIP] Возможно, не установлены библиотеки cuDNN или не хватает памяти (VRAM).")
        return None

def main():
    console.print("[bold cyan]🚀 Universal Transcriber [GPU EDITION][/bold cyan]")
    console.print("[italic white]Оптимизировано для NVIDIA графики (CUDA)[/italic white]\n")

    if not check_cuda():
        if not questionary.confirm("Всё равно продолжить?").ask():
            return

    # 1. Выбор модели
    model_choice = questionary.select(
        "Выберите модель (на GPU можно брать Large):",
        choices=[
            questionary.Choice("Large-v3 (Самая точная)", value="large-v3"),
            questionary.Choice("Medium (Высокая точность)", value="medium"),
            questionary.Choice("Small (Сбалансировано)", value="small"),
            questionary.Choice("Base (Очень быстро)", value="base"),
        ]
    ).ask()

    if not model_choice:
        return

    # 2. Запрос ссылки
    url = Prompt.ask("\n[bold yellow]🔗 Вставьте ссылку на видео/пост[/bold yellow]")

    if not url.startswith("http"):
        console.print("[bold red]Ошибка:[/bold red] Введите корректную ссылку.")
        return

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
