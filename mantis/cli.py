import argparse
import sys
import json
import logging
from typing import Optional, Dict, Any, List
import mantis
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from .models import ProcessingProgress, ExtractionResult
from .utils import MantisError

# Set up logging only for the CLI module, not affecting the library's silent operation
cli_logger = logging.getLogger("mantis.cli")
cli_logger.setLevel(logging.INFO)
if not cli_logger.handlers:
    cli_logger.addHandler(RichHandler(rich_tracebacks=True))

# Load environment variables from .env file
load_dotenv()

# Create console for rich output
console = Console()

def show_progress(progress_data: ProcessingProgress) -> None:
    """Show progress using rich progress bar."""
    # Assert input validation
    assert progress_data is not None, "Progress data cannot be None"
    assert hasattr(progress_data, 'stage'), "Progress data must have a stage attribute"
    assert hasattr(progress_data, 'progress'), "Progress data must have a progress attribute"
    assert isinstance(progress_data.stage, str), "Progress stage must be a string"
    assert isinstance(progress_data.progress, (int, float)), "Progress value must be a number"
    assert 0 <= progress_data.progress <= 1, "Progress value must be between 0 and 1"
    
    console.print(f"[cyan]{progress_data.stage}[/cyan]: {int(progress_data.progress * 100)}%")


def format_output(data: Any) -> str:
    """Format output as text."""
    # Assert input validation
    assert data is not None, "Data cannot be None"
    
    if isinstance(data, str):
        return data
    else:
        # Convert Pydantic model to dict
        data_dict = data.model_dump() if hasattr(data, "model_dump") else data
        result = ""
        for key, value in data_dict.items():
            result += f"{key}: {value}\n"
        return result


def format_transcription(text: str) -> None:
    """Format and print transcription results."""
    # Assert input validation
    assert text is not None, "Transcription text cannot be None"
    assert isinstance(text, str), "Transcription text must be a string"
    
    title = "TRANSCRIPTION"
    console.print(Panel(
        text,
        title=title,
        border_style="cyan",
        padding=(1, 2)
    ))


def format_summary(text: str) -> None:
    """Format and print summary results."""
    # Assert input validation
    assert text is not None, "Summary text cannot be None"
    assert isinstance(text, str), "Summary text must be a string"
    
    title = "SUMMARY"
    console.print(Panel(
        text,
        title=title,
        border_style="magenta",
        padding=(1, 2)
    ))


def format_extraction(result) -> None:
    """Format and print extraction results."""
    # Assert input validation
    assert result is not None, "Extraction result cannot be None"
    
    title = "EXTRACTION RESULTS"
    
    # Handle string results
    if isinstance(result, str):
        console.print(Panel(
            result,
            title=title,
            border_style="yellow",
            padding=(1, 2)
        ))
        return
    
    # Prepare content
    content_lines = []
    
    # Format key points if available
    if hasattr(result, 'key_points') and result.key_points:
        content_lines.append("[bold]KEY POINTS[/bold]")
        for i, point in enumerate(result.key_points, 1):
            content_lines.append(f"{i}. {point}")
        content_lines.append("")
    
    # Format entities if available
    if hasattr(result, 'entities') and result.entities:
        content_lines.append("[bold]ENTITIES[/bold]")
        for entity in result.entities:
            content_lines.append(f"• {entity}")
        content_lines.append("")
    
    # Format summary if available
    if hasattr(result, 'summary') and result.summary:
        content_lines.append("[bold]SUMMARY[/bold]")
        content_lines.append(f"{result.summary}")
        content_lines.append("")
    
    # Format raw text if that's all we have
    if hasattr(result, 'raw_text') and result.raw_text and not (
        (hasattr(result, 'key_points') and result.key_points) or 
        (hasattr(result, 'entities') and result.entities) or 
        (hasattr(result, 'summary') and result.summary)
    ):
        content = result.raw_text
    else:
        content = "\n".join(content_lines)
    
    console.print(Panel(
        content,
        title=title,
        border_style="yellow",
        padding=(1, 2)
    ))


def main():
    parser = argparse.ArgumentParser(description="Mantis CLI: Process audio files with AI")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Transcribe Command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe audio from a file or YouTube URL")
    transcribe_parser.add_argument("audio_source", type=str, help="Path to audio file or YouTube URL")

    # Summarize Command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize audio from a file or YouTube URL")
    summarize_parser.add_argument("audio_source", type=str, help="Path to audio file or YouTube URL")

    # Extract Command
    extract_parser = subparsers.add_parser("extract", help="Extract information from audio")
    extract_parser.add_argument("audio_source", type=str, help="Path to audio file or YouTube URL")
    extract_parser.add_argument("prompt", type=str, help="Custom prompt for extraction")

    args = parser.parse_args()
    
    # Assert command is provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Assert command is valid
    assert args.command in ["transcribe", "summarize", "extract"], f"Invalid command: {args.command}"
    
    # Assert audio_source is provided
    assert hasattr(args, "audio_source"), "Audio source is required"
    assert args.audio_source, "Audio source cannot be empty"
    
    # Assert prompt is provided for extract command
    if args.command == "extract":
        assert hasattr(args, "prompt"), "Prompt is required for extract command"
        assert args.prompt, "Prompt cannot be empty for extract command"
    
    # Configure progress callback
    progress_callback = show_progress

    try:
        if args.command == "transcribe":
            result = mantis.transcribe(
                args.audio_source,
                clean_output=True,  # Always use clean output for better readability
                progress_callback=progress_callback
            )
            # Assert result is not None
            assert result is not None, "Transcription result cannot be None"
            format_transcription(result)

        elif args.command == "summarize":
            result = mantis.summarize(
                args.audio_source,
                progress_callback=progress_callback
            )
            # Assert result is not None
            assert result is not None, "Summary result cannot be None"
            format_summary(result)

        elif args.command == "extract":
            result = mantis.extract(
                args.audio_source,
                args.prompt,
                progress_callback=progress_callback
            )
            # Assert result is not None
            assert result is not None, "Extraction result cannot be None"
            format_extraction(result)

        else:
            parser.print_help()
            sys.exit(1)
            
    except MantisError as e:
        cli_logger.error(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        cli_logger.exception(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
