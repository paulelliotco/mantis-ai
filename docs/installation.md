# Installation Guide

Getting started with Mantis AI is straightforward. This guide will walk you through the installation process and help you set up your environment.

## Prerequisites

Before installing Mantis AI, ensure you have:

- Python 3.9 or higher
- pip (Python package installer)
- A Gemini API key from Google AI Studio

## Installing Mantis AI

### Step 1: Install the Package

Install Mantis AI using pip:

```bash
pip install mantisai
```

This command installs the latest stable version of Mantis AI and all its dependencies.

### Step 2: Set Up Your API Key

Mantis AI uses Google's Gemini API for processing audio. You'll need to set up your API key:

1. Get a Gemini API key from [Google AI Studio](https://ai.google.dev/)
2. Set the API key in your environment:

```bash
# On Linux/macOS
export GEMINI_API_KEY="your-api-key-here"

# On Windows (Command Prompt)
set GEMINI_API_KEY=your-api-key-here

# On Windows (PowerShell)
$env:GEMINI_API_KEY = "your-api-key-here"
```

Alternatively, you can create a `.env` file in your project directory:

```
GEMINI_API_KEY=your-api-key-here
```

### Step 3: Verify Installation

Verify that Mantis AI is installed correctly:

```python
import mantis

# Print the version
print(mantis.__version__)
```

## Optional Dependencies

For YouTube processing, Mantis AI uses yt-dlp which should be installed automatically. If you encounter any issues with YouTube functionality, you can install it manually:

```bash
pip install yt-dlp
```

## Development Installation

If you want to contribute to Mantis AI or install the latest development version:

```bash
# Clone the repository
git clone https://github.com/paulelliotco/mantis-ai.git
cd mantis-ai

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**: Ensure your Gemini API key is correctly set in your environment or `.env` file.

2. **Import Error**: If you encounter import errors, ensure you've installed the package correctly and are using a supported Python version.

3. **YouTube Processing Issues**: If you have problems with YouTube URLs, ensure yt-dlp is installed and up to date.

### Getting Help

If you encounter any issues during installation:

- Check the [GitHub Issues](https://github.com/paulelliotco/mantis-ai/issues) for similar problems
- Open a new issue if your problem hasn't been reported

## Next Steps

Now that you've installed Mantis AI, check out the [Quick Start Guide](quickstart.md) to learn how to use the library. 