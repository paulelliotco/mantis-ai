import argparse
import sys
import mantis
from dotenv import load_dotenv
import rich
from rich.progress import Progress
from rich.console import Console
from rich.table import Table

# Load environment variables from .env file
load_dotenv()

def show_progress(progress: ProcessingProgress):
    console = Console()
    with Progress() as progress:
        task = progress.add_task(f"[cyan]{progress.stage}...", total=100)
        progress.update(task, completed=progress.progress * 100)

def main():
    parser = argparse.ArgumentParser(
        description="Mantis CLI: Process audio files with AI"
    )
    
    # Add batch processing support
    parser.add_argument("--batch", action="store_true", help="Enable batch processing")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker threads")
    
    # Add caching options
    parser.add_argument("--cache-dir", type=str, help="Custom cache directory")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    
    # Add output format options
    parser.add_argument("--format", choices=["text", "json", "table"], default="text")

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
    extract_parser.add_argument("--prompt", type=str, required=True, help="Custom prompt for extraction")

    args = parser.parse_args()

    if args.command == "transcribe":
        try:
            result = mantis.transcribe(args.audio_source)
            print("Transcription Output:")
            print(result.transcription)
        except Exception as e:
            print(f"Error during transcription: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "summarize":
        try:
            result = mantis.summarize(args.audio_source)
            print("Summary Output:")
            print(result.summary)
        except Exception as e:
            print(f"Error during summarization: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "extract":
        try:
            result = mantis.extract(args.audio_source, args.prompt)
            print("Extraction Output:")
            print(result.extraction)
        except Exception as e:
            print(f"Error during extraction: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
