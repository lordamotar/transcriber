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
        console.print("[bold red]ВНИМАНИЕ:[/bold red] NVIDIA GPU не обнаружен. Скрипт может работать некорректно.")
        return False
    console.print(f"[bold green]GPU обнаружен:[/bold green] {torch.cuda.get_device_name(0)}")
    return True

def download_audio(url, progress, task_id):
    """Скачивает аудио высокого качества через ffmpeg."""
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
        progress.update(task_id, description="[bold blue]📥 Скачивание...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_title = info.get('title') or info.get('id') or f"video_{int(time.time())}"
            temp_filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(temp_filename)
            actual_filename = base + ".m4a"
            
            progress.update(task_id, advance=15)
            if os.path.exists(actual_filename):
                return actual_filename, video_title
            return None, None
    except Exception as e:
        console.print(f"[bold red]![/bold red] Ошибка скачивания {url}: {e}")
        return None, None

def get_bar_color(percentage):
    """Цвет в зависимости от процента."""
    if percentage < 25: return "red"
    elif percentage < 50: return "orange3"
    elif percentage < 75: return "yellow"
    else: return "green"

def transcribe_audio(audio_path, model, progress, task_id):
    """Транскрибация на GPU (CUDA)."""
    try:
        progress.update(task_id, description="[bold cyan]⚡ GPU Обработка...")
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        total_duration = info.duration
        full_text = []
        start_points = progress.tasks[task_id].completed
        
        for segment in segments:
            full_text.append(segment.text)
            if total_duration > 0:
                sub_progress = (segment.end / total_duration) * 75
                current_total = min(start_points + sub_progress, 99)
                color = get_bar_color(current_total)
                progress.update(task_id, completed=current_total, 
                                description=f"[bold {color}]⚡ Обработка ({int(current_total)}%)...")

        return " ".join(full_text)
    except Exception as e:
        console.print(f"[bold red]![/bold red] Ошибка GPU транскрибации: {e}")
        return None

def process_url(url, model, model_name):
    """Полный цикл для одной ссылки."""
    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        task_id = progress.add_task(f"[bold red]Запуск {url[:30]}...", total=100)

        # 1. Скачивание
        audio_path, video_title = download_audio(url, progress, task_id)
        if not audio_path: return

        # 2. Транскрибация
        text = transcribe_audio(audio_path, model, progress, task_id)
        
        if text:
            # 3. Сохранение
            progress.update(task_id, description="[bold green]💾 Сохранение...")
            output_filename = f"{clean_filename(video_title)}.txt"
            with open(output_filename, "w", encoding="utf-8") as f:
                f.write(text)
                
            progress.update(task_id, completed=100, description="[bold green]✅ Готово!")
            console.print(f"[bold green]✨ Результат:[/bold green] {output_filename}")
        
        if audio_path and os.path.exists(audio_path):
            try: os.remove(audio_path)
            except: pass

def main():
    console.print("[bold cyan]🚀 Universal Transcriber [GPU EDITION][/bold cyan]\n")

    if not check_cuda():
        if not questionary.confirm("Всё равно продолжить?").ask(): return

    # 1. Выбор модели
    model_size = questionary.select(
        "Выберите модель (GPU потянет Large):",
        choices=[
            questionary.Choice("Large-v3 (Макс. точность)", value="large-v3"),
            questionary.Choice("Medium (Высокая точность)", value="medium"),
            questionary.Choice("Small (Сбалансировано)", value="small"),
            questionary.Choice("Base (Скорость)", value="base"),
        ]
    ).ask()

    if not model_size: return

    # 2. Ввод ссылки или пути к файлу
    user_input = Prompt.ask("\n[bold yellow]🔗 Вставьте ссылку ИЛИ путь к .txt файлу со списком[/bold yellow]").strip()

    urls = []
    if os.path.isfile(user_input):
        console.print(f"[bold blue]📂 Чтение списка из файла...[/bold blue]")
        with open(user_input, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip().startswith("http")]
        console.print(f"[bold blue]Найдено ссылок: {len(urls)}[/bold blue]\n")
    else:
        if user_input.startswith("http"):
            urls = [user_input]
        else:
            console.print("[bold red]Ошибка:[/bold red] Введите корректную ссылку или путь к файлу.")
            return

    if not urls:
        console.print("[bold red]Список пуст.[/bold red]")
        return

    # Загружаем модель один раз на GPU
    console.print(f"[bold magenta]⚙️ Загрузка модели '{model_size}' на GPU...[/bold magenta]")
    model = WhisperModel(model_size, device="cuda", compute_type="float16")

    # 3. Обработка
    for i, url in enumerate(urls, 1):
        if len(urls) > 1:
            console.print(f"\n[bold yellow]>>> Видео {i} из {len(urls)}[/bold yellow]")
        process_url(url, model, model_size)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: console.print("\n[bold red]✖ Остановлено.[/bold red]")
