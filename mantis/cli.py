import argparse
import sys
import json
import logging
from typing import Optional, Dict, Any
import mantis
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
from rich.logging import RichHandler
from .models import ProcessingProgress
from .utils import MantisError

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("mantis.cli")

# Load environment variables from .env file
load_dotenv()

# Create console for rich output
console = Console()

def show_progress(progress_data: ProcessingProgress) -> None:
    """Show progress using rich progress bar."""
    console.print(f"[cyan]{progress_data.stage}[/cyan]: {int(progress_data.progress * 100)}%")


def format_output(data: Any, output_format: str) -> str:
    """Format output based on the specified format."""
    if output_format == "json":
        if isinstance(data, str):
            return json.dumps({"result": data})
        else:
            # Convert Pydantic model to dict
            return json.dumps(data.model_dump() if hasattr(data, "model_dump") else data)
    elif output_format == "table":
        # For table format, we'd need to implement a more complex formatting
        # This is a simple version that just returns key-value pairs
        if isinstance(data, str):
            return data
        else:
            result = ""
            data_dict = data.model_dump() if hasattr(data, "model_dump") else data
            for key, value in data_dict.items():
                result += f"{key}: {value}\n"
            return result
    else:  # Default to text
        return str(data)


def main():
    parser = argparse.ArgumentParser(description="Mantis CLI: Process audio files with AI")

    # Global options
    parser.add_argument("--model", type=str, default="gemini-1.5-flash", 
                        help="Gemini model to use (default: gemini-1.5-flash)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                        help="Enable verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", 
                        help="Suppress progress output")
    parser.add_argument("--raw", action="store_true", 
                        help="Return raw output objects")
    parser.add_argument("--format", choices=["text", "json", "table"], default="text",
                        help="Output format (default: text)")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Transcribe Command
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe audio from a file or YouTube URL")
    transcribe_parser.add_argument("audio_source", type=str, help="Path to audio file or YouTube URL")

    # Summarize Command
    summarize_parser = subparsers.add_parser("summarize", help="Summarize audio from a file or YouTube URL")
    summarize_parser.add_argument("audio_source", type=str, help="Path to audio file or YouTube URL")
    summarize_parser.add_argument("--max-length", type=int, help="Maximum length of summary in characters")

    # Extract Command
    extract_parser = subparsers.add_parser("extract", help="Extract information from audio")
    extract_parser.add_argument("audio_source", type=str, help="Path to audio file or YouTube URL")
    extract_parser.add_argument("--prompt", type=str, required=True, help="Custom prompt for extraction")
    extract_parser.add_argument("--structured", action="store_true", help="Return structured data if possible")

    args = parser.parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger("mantis").setLevel(logging.DEBUG)
    
    # Configure progress callback
    progress_callback = None if args.quiet else show_progress

    try:
        if args.command == "transcribe":
            result = mantis.transcribe(
                args.audio_source,
                raw_output=args.raw,
                model=args.model,
                progress_callback=progress_callback
            )
            console.print(format_output(result, args.format))

        elif args.command == "summarize":
            result = mantis.summarize(
                args.audio_source,
                raw_output=args.raw,
                model=args.model,
                max_length=args.max_length,
                progress_callback=progress_callback
            )
            console.print(format_output(result, args.format))

        elif args.command == "extract":
            result = mantis.extract(
                args.audio_source,
                args.prompt,
                raw_output=args.raw,
                model=args.model,
                structured_output=args.structured,
                progress_callback=progress_callback
            )
            console.print(format_output(result, args.format))

        else:
            parser.print_help()
            sys.exit(1)
            
    except MantisError as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
