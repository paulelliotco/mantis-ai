import argparse
import sys
from mantis.transcription import transcribe
from mantis.summarize import summarize
from mantis.extract import extract
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="Mantis CLI: Transcribe, Summarize, and Extract information from audio files or YouTube URLs."
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Transcribe Command
    transcribe_parser = subparsers.add_parser('transcribe', help='Transcribe audio from a file or YouTube URL')
    transcribe_parser.add_argument('audio_source', type=str, help='Path to audio file or YouTube URL')
    
    # Summarize Command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize audio from a file or YouTube URL')
    summarize_parser.add_argument('audio_source', type=str, help='Path to audio file or YouTube URL')
    
    # Extract Command
    extract_parser = subparsers.add_parser('extract', help='Extract information from audio')
    extract_parser.add_argument('audio_source', type=str, help='Path to audio file or YouTube URL')
    extract_parser.add_argument('--prompt', type=str, required=True, help='Custom prompt for extraction')
    
    args = parser.parse_args()
    
    if args.command == 'transcribe':
        try:
            result = transcribe(args.audio_source)
            print("Transcription Output:")
            print(result.transcription)
        except Exception as e:
            print(f"Error during transcription: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == 'summarize':
        try:
            result = summarize(args.audio_source)
            print("Summary Output:")
            print(result.summary)
        except Exception as e:
            print(f"Error during summarization: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif args.command == 'extract':
        try:
            result = extract(args.audio_source, args.prompt)
            print("Extraction Output:")
            print(result.extraction)
        except Exception as e:
            print(f"Error during extraction: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main() 