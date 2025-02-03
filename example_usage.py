import os
import mantis
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def main():
    try:
        # Example usage for transcription using a local file path
        transcription_result = mantis.transcribe("path/to/your/audio.mp3")
        print("Transcription (Local File):", transcription_result.transcription)

        # Example usage for transcription using a YouTube URL
        youtube_url = "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast"
        transcription_youtube = mantis.transcribe(youtube_url)
        print("\nTranscription (YouTube URL):", transcription_youtube.transcription)

        # Example usage for summarization using a local file path
        summary_result = mantis.summarize("path/to/your/audio.mp3")
        print("\nSummary (Local File):", summary_result.summary)

        # Example usage for summarization using a YouTube URL
        summary_youtube = mantis.summarize(youtube_url)
        print("\nSummary (YouTube URL):", summary_youtube.summary)

        # Example usage for extraction using a local file path and a custom prompt
        extraction_result = mantis.extract("path/to/your/audio.mp3", "Extract key points from this audio.")
        print("\nExtraction (Local File):", extraction_result.extraction)

        # Example usage for extraction using a YouTube URL and a custom prompt
        extraction_youtube = mantis.extract(youtube_url, "Extract key points from this audio.")
        print("\nExtraction (YouTube URL):", extraction_youtube.extraction)
    except Exception as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
