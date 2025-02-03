# Mantis

Mantis is a Python package for transcribing audio files, summarizing text, and extracting information using Gemini AI and Pydantic. It provides simple interfaces to transcribe MP3 files, summarize text, and extract key information effortlessly.

## 📚 Documentation

[![Documentation Status](https://readthedocs.org/projects/mantis/badge/?version=latest)](https://mantis.readthedocs.io/en/latest/?badge=latest)

The comprehensive documentation is available at [https://mantis.readthedocs.io](https://mantis.readthedocs.io).

## 🛠️ Features

- **Easy Transcription**: Transcribe MP3 files or YouTube URLs with a single function call.
- **Data Validation**: Ensures input and output data integrity using Pydantic.
- **Integration with Gemini AI**: Leverages Gemini AI's powerful language models for accurate transcriptions, summaries, and extractions.
- **YouTube Support**: Stream audio directly from YouTube URLs without downloading the entire file.
- **Command-Line Interface (CLI)**: Interact with Mantis directly from the terminal.
- **Comprehensive Testing**: Robust unit tests ensure reliability.
- **Continuous Integration**: Automated testing and linting with GitHub Actions.
- **Comprehensive Documentation**: Generated with Sphinx and hosted on Read the Docs.

## 🚀 Installation

To install Mantis, run the following command:

```bash
pip install mantis
```

Alternatively, install it in editable mode for development purposes:

```bash
pip install -e .
```

## 🧑‍💻 Usage

### 🖥️ Command-Line Interface (CLI)

After installation, you can use the `mantis` CLI to transcribe, summarize, and extract information from audio files or YouTube URLs.

```bash
mantis [command] [arguments]
```

#### **Available Commands:**

- **transcribe**: Transcribe audio from a file or YouTube URL.
- **summarize**: Summarize audio from a file or YouTube URL.
- **extract**: Extract information from audio with a custom prompt.

#### **Examples:**

- **Transcribe a local MP3 file:**

    ```bash
    mantis transcribe path/to/your/audio.mp3
    ```

- **Transcribe a YouTube URL:**

    ```bash
    mantis transcribe https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast
    ```

- **Summarize a local MP3 file:**

    ```bash
    mantis summarize path/to/your/audio.mp3
    ```

- **Summarize a YouTube URL:**

    ```bash
    mantis summarize https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast
    ```

- **Extract information from a local MP3 file with a custom prompt:**

    ```bash
    mantis extract path/to/your/audio.mp3 --prompt "Extract key points from this audio."
    ```

- **Extract information from a YouTube URL with a custom prompt:**

    ```bash
    mantis extract https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast --prompt "Extract key points from this audio."
    ```

### 📝 Python API

You can also use Mantis programmatically in your Python scripts:

```python
import os
from mantis import transcribe, summarize, extract
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    try:
        # Example usage for transcription using a local file path
        transcription_result = transcribe("path/to/your/audio.mp3")
        print("Transcription (Local File):", transcription_result.transcription)

        # Example usage for transcription using a YouTube URL
        youtube_url = "https://www.youtube.com/watch?v=AKJfakEsgy0&ab_channel=MrBeast"
        transcription_youtube = transcribe(youtube_url)
        print("\nTranscription (YouTube URL):", transcription_youtube.transcription)

        # Example usage for summarization using a local file path
        summary_result = summarize("path/to/your/audio.mp3")
        print("\nSummary (Local File):", summary_result.summary)

        # Example usage for summarization using a YouTube URL
        summary_youtube = summarize(youtube_url)
        print("\nSummary (YouTube URL):", summary_youtube.summary)

        # Example usage for extraction using a local file path and a custom prompt
        extraction_result = extract(
            "path/to/your/audio.mp3",
            "Extract key points from this audio."
        )
        print("\nExtraction (Local File):", extraction_result.extraction)

        # Example usage for extraction using a YouTube URL and a custom prompt
        extraction_youtube = extract(
            youtube_url,
            "Extract key points from this audio."
        )
        print("\nExtraction (YouTube URL):", extraction_youtube.extraction)
    except Exception as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
```

## 📦 Installation

To install Mantis, please refer to the [Installation](#installation) section above.

## 🔐 Environment Variables

Mantis requires certain environment variables to function correctly. Please refer to the `.env.example` file for the necessary configurations.

1. **Create a `.env` File:**

    ```bash
    cp .env.example .env
    ```

2. **Fill in the Required Values:**

    Open the `.env` file in your preferred text editor and replace the placeholder values with your actual credentials.

    ```plaintext
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

**Note:** Ensure that your `.env` file is added to `.gitignore` to prevent accidental exposure of sensitive information.

## 📄 License

This project is licensed under the [Apache License 2.0](LICENSE).

## 🙌 Contributing

Contributions are welcome! Please refer to the [CONTRIBUTING](CONTRIBUTING.md) guide for more details.

## 📜 Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md) to understand our expectations for participant behavior.


