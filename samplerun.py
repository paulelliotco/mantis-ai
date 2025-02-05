# Basic transcription
import mantis

# Access the transcription field directly
result = mantis.transcribe("tests/sample_audio/sample_audio.mp3")
print(result)

# Summarization
#mantis summarize path/to/your/audio.mp3

# Extract specific information
#mantis extract path/to/your/audio.mp3 --prompt "List all action items mentioned"

# Using different output formats
#mantis transcribe path/to/your/audio.mp3 --format json
#mantis transcribe path/to/your/audio.mp3 --format table

# With caching disabled
#mantis transcribe path/to/your/audio.mp3 --no-cache
