import mantis
import os
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table

# Initialize console for rich output
console = Console()

def process_with_spinner(func, *args, **kwargs):
    """Execute a function with a spinner to show progress."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(description="Processing...", total=None)
        result = func(*args, **kwargs)
        progress.update(task, completed=True)
        return result

def display_header():
    """Display the application header."""
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]Mantis AI[/bold green]: Audio Processing with Large Language Models",
        title="Client Demo",
        border_style="green",
        padding=(1, 2)
    ))
    console.print("\n")

def display_features():
    """Display the key features of Mantis."""
    table = Table(title="Key Features", show_header=True, header_style="bold magenta")
    table.add_column("Feature", style="cyan")
    table.add_column("Description", style="white")
    
    table.add_row("Audio Transcription", "Convert audio files to text")
    table.add_row("Text Summarization", "Generate concise summaries of audio content")
    table.add_row("Information Extraction", "Retrieve specific details using custom prompts")
    table.add_row("YouTube Support", "Process YouTube URLs directly")
    
    console.print(table)
    console.print("\n")

def get_audio_source():
    """Get the audio source from the user (local file or YouTube URL)."""
    source_type = Prompt.ask(
        "Select audio source type",
        choices=["1", "2"],
        default="1"
    )
    
    if source_type == "1":
        console.print("[cyan]Using local audio file...[/cyan]")
        return "C:\\Users\\paule\\Music\\test.mp3"
    else:
        youtube_url = Prompt.ask(
            "Enter YouTube URL",
            default="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
        console.print(f"[cyan]Using YouTube URL: {youtube_url}[/cyan]")
        return youtube_url

def transcribe_demo(audio_source: str):
    """Run the transcription demo."""
    console.print("[bold blue]DEMO 1: Audio Transcription[/bold blue]")
    console.print("Converting audio to text...\n")
    
    is_youtube = audio_source.startswith("http")
    source_type = "YouTube video" if is_youtube else "audio file"
    
    console.print(f"Transcribing {source_type}...\n")
    
    # Always use clean output for better readability
    transcript = process_with_spinner(mantis.transcribe, audio_source, clean_output=True)
    
    console.print(Panel(
        transcript,
        title=f"Transcription Result ({source_type})",
        border_style="cyan",
        padding=(1, 2)
    ))
    console.print("\n")
    
    return transcript

def summarize_demo(audio_source: str):
    """Run the summarization demo."""
    console.print("[bold blue]DEMO 2: Audio Summarization[/bold blue]")
    console.print("Generating a concise summary...\n")
    
    is_youtube = audio_source.startswith("http")
    source_type = "YouTube video" if is_youtube else "audio file"
    
    console.print(f"Summarizing {source_type}...\n")
    
    summary = process_with_spinner(mantis.summarize, audio_source)
    
    console.print(Panel(
        summary,
        title=f"Summary Result ({source_type})",
        border_style="magenta",
        padding=(1, 2)
    ))
    console.print("\n")
    
    return summary

def extract_demo(audio_source: str):
    """Run the extraction demo with custom prompts."""
    console.print("[bold blue]DEMO 3: Information Extraction[/bold blue]")
    
    is_youtube = audio_source.startswith("http")
    source_type = "YouTube video" if is_youtube else "audio file"
    
    # Predefined extraction prompts
    if is_youtube:
        extraction_prompt = "Identify the key themes and messages in this content"
    else:
        extraction_prompt = "Identify the mood and setting described in this audio"
    
    console.print(f"\nExtracting information using prompt: [italic]\"{extraction_prompt}\"[/italic]\n")
    
    extraction = process_with_spinner(mantis.extract, audio_source, extraction_prompt)
    
    # Display extraction results
    if hasattr(extraction, 'raw_text'):
        result_text = extraction.raw_text
    else:
        result_text = str(extraction)
    
    console.print(Panel(
        result_text,
        title=f"Extraction Result ({source_type})",
        border_style="yellow",
        padding=(1, 2)
    ))
    console.print("\n")

def main():
    # Display header and features
    display_header()
    display_features()
    
    # Pause for effect
    time.sleep(1)
    
    # Display source selection options
    console.print("[bold]Select Audio Source:[/bold]")
    console.print("1. Local audio file (poem reading)")
    console.print("2. YouTube URL")
    console.print("\n")
    
    # Get audio source
    audio_source = get_audio_source()
    
    # Check if local file exists
    if not audio_source.startswith("http") and not os.path.exists(audio_source):
        console.print(f"[red]Error: File {audio_source} not found.[/red]")
        return
    
    # Run the demos
    transcript = transcribe_demo(audio_source)
    
    # Pause between demos
    time.sleep(1)
    
    summary = summarize_demo(audio_source)
    
    # Pause between demos
    time.sleep(1)
    
    extract_demo(audio_source)
    
    # Display conclusion
    console.print(Panel.fit(
        "[bold green]Demo completed successfully![/bold green]\n\n"
        "Mantis AI provides a simple yet powerful API for processing audio content.",
        title="Thank You",
        border_style="green",
        padding=(1, 2)
    ))

if __name__ == "__main__":
    main() 